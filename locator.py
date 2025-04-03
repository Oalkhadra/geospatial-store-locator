from flask import Flask, request, render_template, jsonify
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
import json
import os

app = Flask(__name__)


# Load data
def load_data():
    # Change path as needed
    return pd.read_csv('./Data/geocoded_stores_complete.csv')


# Store Finder class
class StoreFinderKNN:
    def __init__(self, store_data):
        self.store_data = store_data
        self.coordinates = self.store_data[['latitude', 'longitude']].values
        self.knn_model = None

    def fit_knn_model(self):
        if len(self.coordinates) == 0:
            raise ValueError("No valid coordinates found in the store data.")

        self.knn_model = NearestNeighbors(algorithm='ball_tree', metric='haversine')
        self.knn_model.fit(np.radians(self.coordinates))

        return self.knn_model

    def find_nearest_stores(self, query_location, k):
        if self.knn_model is None:
            self.fit_knn_model()

        # Prepare query coordinates
        query_coords = np.array([query_location])

        # Find k nearest neighbors
        distances, indices = self.knn_model.kneighbors(
            np.radians(query_coords),
            n_neighbors=min(k, len(self.coordinates))
        )

        # Convert distances from radians to miles (Earth radius in miles ≈ 3958.8)
        distances = distances[0] * 3958.8

        # Get the nearest stores
        nearest_stores = self.store_data.iloc[indices[0]].copy()
        nearest_stores['distance_miles'] = distances

        return nearest_stores[['Store_Num', 'Account_Name', 'Address', 'City',
                               'State', 'Zip', 'distance_miles', 'latitude', 'longitude']]


# Initialize data and model
store_data = load_data()
finder = StoreFinderKNN(store_data)
finder.fit_knn_model()  # Pre-fit the model to avoid delays


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/find_stores', methods=['POST'])
def find_stores():
    try:
        # Get data from form
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        num_stores = int(request.form['num_stores'])

        # Find nearest stores
        nearest_stores = finder.find_nearest_stores((latitude, longitude), k=num_stores)

        # Convert to dictionary for JSON
        nearest_stores['distance_miles'] = nearest_stores['distance_miles'].round(2)
        stores_list = nearest_stores.to_dict('records')

        # Create a GeoJSON object for the map
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [row['longitude'], row['latitude']]
                    },
                    "properties": {
                        "Store_Num": str(row['Store_Num']),
                        "Account_Name": str(row['Account_Name']),
                        "Address": str(row['Address']),
                        "City": str(row['City']),
                        "State": str(row['State']),
                        "Zip": str(row['Zip']),
                        "distance_miles": str(row['distance_miles'])
                    }
                } for _, row in nearest_stores.iterrows()
            ]
        }

        return render_template(
            'results.html',
            stores=stores_list,
            latitude=latitude,
            longitude=longitude,
            geojson=json.dumps(geojson)
        )

    except Exception as e:
        return render_template('index.html', error=str(e))


# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

# Create HTML templates
with open('templates/index.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Store Locator</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
    <style>
        body {
            padding: 20px;
        }
        .container {
            max-width: 800px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Store Locator</h1>
        <p class="lead">Enter coordinates to find the nearest stores.</p>

        {% if error %}
        <div class="alert alert-danger">{{ error }}</div>
        {% endif %}

        <form action="/find_stores" method="post" class="mb-4">
            <div class="row mb-3">
                <div class="col-md-6">
                    <label for="latitude" class="form-label">Latitude</label>
                    <input type="number" step="any" class="form-control" id="latitude" name="latitude" value="34.098942" required>
                </div>
                <div class="col-md-6">
                    <label for="longitude" class="form-label">Longitude</label>
                    <input type="number" step="any" class="form-control" id="longitude" name="longitude" value="-118.323040" required>
                </div>
            </div>
            <div class="mb-3">
                <label for="num_stores" class="form-label">Number of stores to find</label>
                <input type="number" class="form-control" id="num_stores" name="num_stores" min="1" max="100" value="10" required>
            </div>
            <button type="submit" class="btn btn-primary">Find Nearest Stores</button>
        </form>

        <div class="card mb-4">
            <div class="card-header">Not sure about coordinates?</div>
            <div class="card-body">
                <p>You can find the latitude and longitude of any location using <a href="https://www.google.com/maps" target="_blank">Google Maps</a>:</p>
                <ol>
                    <li>Right-click on a location</li>
                    <li>Select "What's here?"</li>
                    <li>The coordinates will appear at the bottom of the screen</li>
                </ol>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

with open('templates/results.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Store Locator Results</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <style>
        body {
            padding: 20px;
        }
        .container {
            max-width: 1000px;
        }
        #map {
            height: 400px;
            margin-bottom: 20px;
        }
        th {
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Store Locator Results</h1>

        <div id="map"></div>

        <h2>Nearest Stores</h2>
        <p>Showing nearest stores to coordinates ({{ latitude }}, {{ longitude }})</p>

        <div class="table-responsive mb-4">
            <table class="table table-striped table-hover" id="storesTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">Store #</th>
                        <th onclick="sortTable(1)">Name</th>
                        <th onclick="sortTable(2)">Address</th>
                        <th onclick="sortTable(3)">City</th>
                        <th onclick="sortTable(4)">State</th>
                        <th onclick="sortTable(5)">Zip</th>
                        <th onclick="sortTable(6)">Distance (miles)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for store in stores %}
                    <tr>
                        <td>{{ store.Store_Num }}</td>
                        <td>{{ store.Account_Name }}</td>
                        <td>{{ store.Address }}</td>
                        <td>{{ store.City }}</td>
                        <td>{{ store.State }}</td>
                        <td>{{ store.Zip }}</td>
                        <td>{{ store.distance_miles }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="mb-4">
            <button class="btn btn-success" onclick="exportToCSV()">Download as CSV</button>
            <a href="/" class="btn btn-primary">Search Again</a>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
        // Initialize the map
        var map = L.map('map').setView([{{ latitude }}, {{ longitude }}], 11);

        // Add a tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // Add a marker for the search location
        L.marker([{{ latitude }}, {{ longitude }}])
            .bindPopup("Your location")
            .addTo(map);

        // Add markers for the stores
        var geojson = {{ geojson|safe }};

        L.geoJSON(geojson, {
            pointToLayer: function(feature, latlng) {
                return L.marker(latlng);
            },
            onEachFeature: function(feature, layer) {
                var props = feature.properties;
                layer.bindPopup(
                    "<strong>" + props.Account_Name + "</strong><br>" +
                    props.Address + "<br>" +
                    props.City + ", " + props.State + " " + props.Zip + "<br>" +
                    "Distance: " + props.distance_miles + " miles"
                );
            }
        }).addTo(map);

        // Function to sort the table
        function sortTable(n) {
            var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
            table = document.getElementById("storesTable");
            switching = true;
            // Set the sorting direction to ascending
            dir = "asc";

            while (switching) {
                switching = false;
                rows = table.rows;

                for (i = 1; i < (rows.length - 1); i++) {
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[n];
                    y = rows[i + 1].getElementsByTagName("TD")[n];

                    // Check if the two rows should switch
                    if (dir == "asc") {
                        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                            shouldSwitch = true;
                            break;
                        }
                    } else if (dir == "desc") {
                        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                            shouldSwitch = true;
                            break;
                        }
                    }
                }

                if (shouldSwitch) {
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount++;
                } else {
                    if (switchcount == 0 && dir == "asc") {
                        dir = "desc";
                        switching = true;
                    }
                }
            }
        }

        // Function to export table to CSV
        function exportToCSV() {
            var table = document.getElementById("storesTable");
            var csv = [];

            // Get headers
            var headers = [];
            var headerCells = table.rows[0].cells;
            for (var i = 0; i < headerCells.length; i++) {
                headers.push(headerCells[i].textContent.trim());
            }
            csv.push(headers.join(','));

            // Get data
            for (var i = 1; i < table.rows.length; i++) {
                var row = [];
                var cells = table.rows[i].cells;
                for (var j = 0; j < cells.length; j++) {
                    var value = cells[j].textContent.trim();
                    // Quote values that contain commas
                    if (value.indexOf(',') > -1) {
                        value = '"' + value + '"';
                    }
                    row.push(value);
                }
                csv.push(row.join(','));
            }

            // Download CSV
            var csvContent = csv.join('\\n');
            var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            var link = document.createElement("a");
            var url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", "nearest_stores.csv");
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)