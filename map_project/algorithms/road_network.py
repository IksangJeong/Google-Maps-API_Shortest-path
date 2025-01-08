import requests

def get_road_data(start, end):
    """
    OSRM API에서 출발지와 도착지 간의 경로 데이터를 가져오는 함수.
    """
    OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving/"
    start_coords = f"{start['lng']},{start['lat']}"
    end_coords = f"{end['lng']},{end['lat']}"
    url = f"{OSRM_BASE_URL}{start_coords};{end_coords}?overview=full&geometries=geojson"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # OSRM 응답 디버깅 출력
        print("OSRM Response:", data)

        if "routes" in data and len(data["routes"]) > 0:
            route = data["routes"][0]
            return {
                "distance": route["distance"],
                "duration": route["duration"],
                "geometry": route["geometry"]["coordinates"]
            }
        else:
            raise ValueError("No valid route found in OSRM response.")
    except Exception as e:
        print(f"Error fetching road data: {e}")
        return None
