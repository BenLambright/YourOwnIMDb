from flask import Blueprint, render_template, request
from app.database import Database

queries_bp = Blueprint("query", __name__)

# Query 1
@queries_bp.route("/list_tables")
def list_tables():
    """List all tables in the database."""

    # >>>> TODO 1: Write a query to list all the tables in the database. <<<<

    query = """show tables;"""

    with Database() as db:
        tables = db.execute(query)
    return render_template("list_tables.html", tables=tables)

# Query 2
@queries_bp.route("/search_movie", methods=["POST"])
def search_movie():
    """Search for movies by name."""
    movie_name = request.form["movie_name"]

    # >>>> TODO 2: Search Motion Picture by Motion picture name. <<<<
    #              List the movie `name`, `rating`, `production` and `budget`.

    query = """SELECT name, rating, production, budget FROM MotionPicture WHERE name LIKE %s;"""
    
    with Database() as db:
        movies = db.execute(query, (f"%{movie_name}%",))
    return render_template("search_results.html", movies=movies)


@queries_bp.route("/search_liked_movies", methods=["POST"])
def search_liked_movies():
    """Search for movies liked by a specific user."""
    user_email = request.form["user_email"]
    assert(type(user_email)==str)

    # >>>> TODO 3: Find the movies that have been liked by a specific user’s email. <<<<
    #              List the movie `name`, `rating`, `production` and `budget`.

    query = """ SELECT mp.name, mp.rating, mp.production, mp.budget
                FROM MotionPicture mp, Likes l
                WHERE l.uemail = %s AND l.mpid = mp.id"""

    with Database() as db:
        movies = db.execute(query, (user_email,))
    return render_template("search_results.html", movies=movies)


@queries_bp.route("/search_by_country", methods=["POST"])
def search_by_country():
    """Search for movies by country using the Location table."""
    country = request.form["country"]

    # >>>> TODO 4: Search motion pictures by their shooting location country. <<<<
    #              List only the motion picture names without any duplicates.

    query = """SELECT DISTINCT name FROM MotionPicture JOIN Location ON country = %s;"""

    with Database() as db:
        movies = db.execute(query, (country,))
    return render_template("search_results_by_country.html", movies=movies)


@queries_bp.route("/search_directors_by_zip", methods=["POST"])
def search_directors_by_zip():
    """Search for directors and the series they directed by zip code."""
    zip_code = request.form["zip_code"]

    # >>>> TODO 5: List all directors who have directed TV series shot in a specific zip code. <<<<
    #              List the director name and TV series name only without duplicates.

    query = """SELECT DISTINCT P.name, MP.name 
                FROM People P JOIN Role R on P.id = R.pid 
                JOIN MotionPicture MP on R.mpid = MP.id 
                WHERE R.role_name = "director" 
                and R.mpid IN (
                            SELECT L.mpid 
                            FROM Location L Join Series S 
                                ON L.mpid = S.mpid 
                            WHERE L.zip = %s); """
    
    with Database() as db:
        results = db.execute(query, (zip_code,))
    return render_template("search_directors_results.html", results=results)


@queries_bp.route("/search_awards", methods=["POST"])
def search_awards():
    """Search for award records where the award count is greater than `k`."""
    k = int(request.form["k"])

    # >>>> TODO 6: Find the people who have received more than “k” awards for a single motion picture in the same year. <<<<
    #              List the person `name`, `motion picture name`, `award year` and `award count`.

    # notes:
    # imma have to join people to get name, motion picture to get motion picture name, and count(mpid)
    # then do count(pid) > %s and award. We will have to do count(pid) > %s, group by year
    # select pid, award_year, count(pid) from award group by award_year having Count(pid) > 3;
    # select p.name, m.name, award_year, count(name) from Award a join People p on p.id = (select pid from award where count(pid

    query = """SELECT p.name, m.name, award_year, count(a.pid)
                FROM Award a 
                JOIN People p ON p.id = a.pid
                JOIN MotionPicture m ON a.mpid = m.id
                GROUP BY award_year
                HAVING COUNT(pid) > %s;
                """

    with Database() as db:
        results = db.execute(query, (k,))
    return render_template("search_awards_results.html", results=results)


@queries_bp.route("/find_youngest_oldest_actors", methods=["GET"])
def find_youngest_oldest_actors():
    """
    Find the youngest and oldest actors based on the difference 
    between the award year and their date of birth.
    """

    # >>>> TODO 7: Find the youngest and oldest actors to win at least one award. <<<<
    #              List the actor names and their age (at the time they received the award). 
    #              The age should be computed from the person’s date of birth to the award winning year only. 
    #              In case of a tie, list all of them.

    query = """
            SELECT P.name, A.award_year - YEAR(P.dob) AS age
            FROM Award A
            JOIN People P ON P.id = A.pid
            JOIN Role R ON P.id = R.pid
            WHERE R.role_name = 'actor'
            AND (A.award_year - YEAR(P.dob) = (
                SELECT MIN(A2.award_year - YEAR(P2.dob))
                FROM Award A2
                JOIN People P2 ON P2.id = A2.pid
                JOIN Role R2 ON P2.id = R2.pid
                WHERE R2.role_name = 'actor'
            )
            OR A.award_year - YEAR(P.dob) = (
                SELECT MAX(A3.award_year - YEAR(P3.dob))
                FROM Award A3
                JOIN People P3 ON P3.id = A3.pid
                JOIN Role R3 ON P3.id = R3.pid
                WHERE R3.role_name = 'actor'
            ));


             """

    with Database() as db:
        actors = db.execute(query)
    
    # Filter out actors with null ages (if any)
    actors = [actor for actor in actors if actor[1] is not None]
    if actors:
        min_age = min(actors, key=lambda x: x[1])[1]
        max_age = max(actors, key=lambda x: x[1])[1]
        youngest_actors = [actor for actor in actors if actor[1] == min_age]
        oldest_actors = [actor for actor in actors if actor[1] == max_age]
        return render_template(
            "actors_by_age.html",
            youngest_actors=youngest_actors,
            oldest_actors=oldest_actors,
        )
    else:
        return render_template(
            "actors_by_age.html", youngest_actors=[], oldest_actors=[]
        )


@queries_bp.route("/search_producers", methods=["POST"])
def search_producers():
    """
    Search for American producers based on a minimum box office collection and maximum budget.
    """
    box_office_min = float(request.form["box_office_min"])
    budget_max = float(request.form["budget_max"])

    # >>>> TODO 8: Find the American [USA] Producers who had a box office collection of more than or equal to “X” with a budget less than or equal to “Y”. <<<< 
    #              List the producer `name`, `movie name`, `box office collection` and `budget`.

    # needs Movie, Role, People, MotionPicture

    query = """
    SELECT p.name, mp.name, boxoffice_collection, budget
    FROM MotionPicture mp
    JOIN Role r ON mp.id = r.mpid AND role_name = "Producer"
    JOIN People p ON p.id = r.pid AND nationality = "USA"
    JOIN Movie m ON mp.id = m.mpid AND boxoffice_collection >= %s
    WHERE mp.budget <= %s
    """

    with Database() as db:
        results = db.execute(query, (box_office_min, budget_max))
    return render_template("search_producers_results.html", results=results)


@queries_bp.route("/search_multiple_roles", methods=["POST"])
def search_multiple_roles():
    """
    Search for people who have multiple roles in movies with a rating above a given threshold.
    """
    rating_threshold = float(request.form["rating_threshold"])

    # >>>> TODO 9: List the people who have played multiple roles in a motion picture where the rating is more than “X”. <<<<
    #              List the person’s `name`, `motion picture name` and `count of number of roles` for that particular motion picture.

    query = """SELECT P.name, MP.name, COUNT(DISTINCT R.role_name) AS role_count
                FROM MotionPicture MP
                JOIN Role R ON MP.id = R.mpid
                JOIN People P ON P.id = R.pid 
                WHERE MP.rating > %s
                GROUP BY P.name, MP.name
                HAVING COUNT(DISTINCT R.role_name) > 1;
                """

    with Database() as db:
        results = db.execute(query, (rating_threshold,))
    return render_template("search_multiple_roles_results.html", results=results)


@queries_bp.route("/top_thriller_movies_boston", methods=["GET"])
def top_thriller_movies_boston():
    """Display the top 2 thriller movies in Boston based on rating."""

    # >>>> TODO 10: Find the top 2 rates thriller movies (genre is thriller) that were shot exclusively in Boston. <<<<
    #               This means that the movie cannot have any other shooting location. 
    #               List the `movie names` and their `ratings`.

    # needs Genre, MotionPicture, Location
    # I need to use an aggregate function when ensuring the city is Boston in the HAVING condition

    query = """
    SELECT mp.name, rating
    FROM Location l
    Join MotionPicture mp ON l.mpid = mp.id
    JOIN Genre g ON l.mpid = g.mpid AND genre_name = "Thriller"
    GROUP BY l.mpid
    HAVING COUNT(DISTINCT city) = 1 AND MIN(city) = "Boston"
    ORDER BY mp.rating DESC
    LIMIT 2
    """

    with Database() as db:
        results = db.execute(query)
    return render_template("top_thriller_movies_boston.html", results=results)



@queries_bp.route("/search_movies_by_likes", methods=["POST"])
def search_movies_by_likes():
    """
    Search for movies that have received more than a specified number of likes,
    where the liking users are below a certain age.
    """
    min_likes = int(request.form["min_likes"])
    max_age = int(request.form["max_age"])

    # >>>> TODO 11: Find all the movies with more than “X” likes by users of age less than “Y”. <<<<
    #               List the movie names and the number of likes by those age-group users.

    query = """ SELECT MP.name, Count(L.uemail)
                FROM MotionPicture MP JOIN Movie M ON MP.id = M.mpid 
                 JOIN Likes L ON MP.id = L.mpid JOIN Users U ON U.email = L.uemail 
                WHERE U.age> %s
                GROUP BY MP.name
                HAVING Count(L.uemail)>%s"""

    with Database() as db:
        results = db.execute(query, (max_age, min_likes))
    return render_template("search_movies_by_likes_results.html", results=results)


@queries_bp.route("/actors_marvel_warner", methods=["GET"])
def actors_marvel_warner():
    """
    List actors who have appeared in movies produced by both Marvel and Warner Bros.
    """

    # >>>> TODO 12: Find the actors who have played a role in both “Marvel” and “Warner Bros” productions. <<<<
    #               List the `actor names` and the corresponding `motion picture names`.

    # needs: Role, MotionPicture, People

    query = """
    SELECT p.name, mp.name
    FROM MotionPicture mp
    JOIN Role r ON r.mpid = mp.id and role_name = "Actor"
    JOIN People p ON r.pid = p.id
    WHERE p.name IN (
    SELECT p.name
    FROM MotionPicture mp
    JOIN Role r ON r.mpid = mp.id and role_name = "Actor"
    JOIN People p ON r.pid = p.id
    WHERE production = "Marvel"
    INTERSECT 
    SELECT p.name
    FROM MotionPicture mp
    JOIN Role r ON r.mpid = mp.id and role_name = "Actor"
    JOIN People p ON r.pid = p.id
    WHERE production = "Warner Bros"
    )
    """

    with Database() as db:
        results = db.execute(query)
    return render_template("actors_marvel_warner.html", results=results)


@queries_bp.route("/movies_higher_than_comedy_avg", methods=["GET"])
def movies_higher_than_comedy_avg():
    """
    Display movies whose rating is higher than the average rating of comedy movies.
    """

    # >>>> TODO 13: Find the motion pictures that have a higher rating than the average rating of all comedy (genre) motion pictures. <<<<
    #               Show the names and ratings in descending order of ratings.

    query = """
                SELECT MP.name, MP.rating
                FROM MotionPicture MP
                WHERE MP.rating > (SELECT AVG(DISTINCT MP.rating)
                                    FROM MotionPicture MP JOIN Genre G 
                                    ON MP.id = G.mpid
                                    WHERE G.genre_name = "comedy")
                ORDER BY MP.rating DESC;
            """

    with Database() as db:
        results = db.execute(query)
    return render_template("movies_higher_than_comedy_avg.html", results=results)


@queries_bp.route("/top_5_movies_people_roles", methods=["GET"])
def top_5_movies_people_roles():
    """
    Display the top 5 movies that involve the most people and roles.
    """

    # >>>> TODO 14: Find the top 5 movies with the highest number of people playing a role in that movie. <<<<
    #               Show the `movie name`, `people count` and `role count` for the movies.

    # needs: MotionPicture, People, Role

    query = """
    SELECT mp.name, COUNT(DISTINCT p.id) as people_count, COUNT(r.role_name) as roles_count
    FROM MotionPicture mp
    JOIN Role r ON r.mpid = mp.id
    JOIN People p ON r.pid = p.id
    GROUP BY mp.id
    ORDER BY COUNT(DISTINCT r.pid) DESC
    LIMIT 5
    """

    with Database() as db:
        results = db.execute(query)
    return render_template("top_5_movies_people_roles.html", results=results)


@queries_bp.route("/actors_with_common_birthday", methods=["GET"])
def actors_with_common_birthday():
    """
    Find pairs of actors who share the same birthday.
    """

    # >>>> TODO 15: Find actors who share the same birthday. <<<<
    #               List the actor names (actor 1, actor 2) and their common birthday.

    query = """ SELECT DISTINCT P1.name AS actor_1, P2.name AS actor_2, P1.dob AS shared_dob
                FROM People P1 JOIN People P2 
                    ON P1.dob = P2.dob AND P1.id < P2.id JOIN Role R1 
                    ON P1.id = R1.pid JOIN Role R2 
                    ON P2.id = R2.pid
                WHERE R1.role_name = 'actor' AND R2.role_name = 'actor';
                """

    with Database() as db:
        results = db.execute(query)
    return render_template("actors_with_common_birthday.html", results=results)
