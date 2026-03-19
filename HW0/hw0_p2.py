# 設定檔案路徑
file_path = r'D:\download\AN4114011_hw0\IMDB-Movie-Data.csv'

# 定義一個函式來讀取CSV檔
def read_csv(file_path):
    with open(file_path, encoding='utf-8') as file:
        lines = file.readlines()
    header = lines[0].strip().split(',')
    data = [line.strip().split(',') for line in lines[1:]]
    return header, data

# 將資料讀取並處理
header, data = read_csv(file_path)

# Helper function to get index of a column by name
def get_column_index(header, column_name):
    return header.index(column_name)

# 問題1: 找出2016年評分最高的前三部電影
def top_3_movies_2016(header, data):
    year_idx = get_column_index(header, 'Year')
    rating_idx = get_column_index(header, 'Rating')
    title_idx = get_column_index(header, 'Title')
    
    movies_2016 = [row for row in data if row[year_idx] == '2016']
    movies_2016_sorted = sorted(movies_2016, key=lambda x: float(x[rating_idx]), reverse=True)
    return [movie[title_idx] for movie in movies_2016_sorted[:3]]

# 問題2: 計算平均收入最高的演員
# 定義: 我們根據每位演員參與的電影收入平均來計算
# 平均收入 = 該演員出演的所有電影的收入總和 / 電影數量
def highest_avg_revenue_actor(header, data):
    revenue_idx = get_column_index(header, 'Revenue (Millions)')
    actors_idx = get_column_index(header, 'Actors')
    
    actor_revenue = {}
    
    for row in data:
        if row[revenue_idx] == '':
            continue
        revenue = float(row[revenue_idx])
        actors = row[actors_idx].split('|')
        
        for actor in actors:
            actor = actor.strip()
            if actor not in actor_revenue:
                actor_revenue[actor] = []
            actor_revenue[actor].append(revenue)
    
    avg_revenue = {actor: sum(revs) / len(revs) for actor, revs in actor_revenue.items()}
    return max(avg_revenue, key=avg_revenue.get)

# 問題3: 計算Emma Watson電影的平均評分
def emma_watson_avg_rating(header, data):
    actors_idx = get_column_index(header, 'Actors')
    rating_idx = get_column_index(header, 'Rating')
    
    emma_watson_movies = [row for row in data if 'Emma Watson' in row[actors_idx]]
    ratings = [float(row[rating_idx]) for row in emma_watson_movies]
    return sum(ratings) / len(ratings) if ratings else 0

# 問題4: 找出與最多演員合作的前三名導演
def top_3_directors_most_actors(header, data):
    director_idx = get_column_index(header, 'Director')
    actors_idx = get_column_index(header, 'Actors')
    
    director_actors = {}
    
    for row in data:
        director = row[director_idx].strip()
        actors = set(row[actors_idx].split('|'))
        
        if director not in director_actors:
            director_actors[director] = set()
        director_actors[director].update(actors)
    
    director_actor_count = {director: len(actors) for director, actors in director_actors.items()}
    sorted_directors = sorted(director_actor_count, key=director_actor_count.get, reverse=True)
    
    return sorted_directors[:3]

# 問題5: 找出參演最多類型電影的前兩名演員
def top_2_actors_most_genres(header, data):
    genre_idx = get_column_index(header, 'Genre')
    actors_idx = get_column_index(header, 'Actors')
    
    actor_genres = {}
    
    for row in data:
        genres = set(row[genre_idx].split('|'))  # 獲取該電影的所有類型（使用set避免重複類型）
        actors = row[actors_idx].split('|')  # 獲取該電影的所有演員
        
        for actor in actors:
            actor = actor.strip()
            if actor not in actor_genres:
                actor_genres[actor] = set()  # 為每位演員建立一個類型集合
            actor_genres[actor].update(genres)  # 更新該演員參演的類型集合
    
    # 計算每位演員參演的獨特類型數量，並排序
    actor_genre_count = {actor: len(genres) for actor, genres in actor_genres.items()}
    sorted_actors = sorted(actor_genre_count, key=actor_genre_count.get, reverse=True)
    
    return sorted_actors[:2]  # 回傳參演最多類型的前兩名演員

# 問題6: 找出電影年份最大差距的演員
def actors_largest_max_gap(header, data):
    year_idx = get_column_index(header, 'Year')
    actors_idx = get_column_index(header, 'Actors')
    
    actor_years = {}
    
    for row in data:
        year = int(row[year_idx])
        actors = row[actors_idx].split('|')
        
        for actor in actors:
            actor = actor.strip()
            if actor not in actor_years:
                actor_years[actor] = []
            actor_years[actor].append(year)
    
    max_gap = {}
    
    for actor, years in actor_years.items():
        if len(years) > 1:
            max_gap[actor] = max(years) - min(years)
    
    max_gap_value = max(max_gap.values())
    return [actor for actor, gap in max_gap.items() if gap == max_gap_value]

# 問題7: 找出與Johnny Depp直接或間接合作的演員
def johnny_depp_collaborators(header, data):
    actors_idx = get_column_index(header, 'Actors')
    
    # 建立合作網絡
    actor_collabs = {}
    
    for row in data:
        actors = [actor.strip() for actor in row[actors_idx].split('|')]
        
        for i, actor in enumerate(actors):
            if actor not in actor_collabs:
                actor_collabs[actor] = set()
            actor_collabs[actor].update(actors[:i] + actors[i+1:])
    
    # 找出與Johnny Depp合作的演員（直接和間接）
    def find_collaborators(actor, collabs):
        visited = set()
        to_visit = [actor]
        
        while to_visit:
            current_actor = to_visit.pop(0)
            if current_actor not in visited:
                visited.add(current_actor)
                to_visit.extend(collabs[current_actor] - visited)
        
        return visited
    
    collaborators = find_collaborators('Johnny Depp', actor_collabs)
    collaborators.remove('Johnny Depp')
    return collaborators

# 印出每一題的答案
print("問題1:", top_3_movies_2016(header, data))
print("問題2:", highest_avg_revenue_actor(header, data))
print("問題3:", emma_watson_avg_rating(header, data))
print("問題4:", top_3_directors_most_actors(header, data))
print("問題5:", top_2_actors_most_genres(header, data))
print("問題6:", actors_largest_max_gap(header, data))
print("問題7:", johnny_depp_collaborators(header, data))
