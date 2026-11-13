import unittest
import json

def create_cell_id(south, west, north, east):
    return (
        f'cell_{south:.6f}_{west:.6f}_'
        f'{north:.6f}_{east:.6f}'
    )

def generate_grid(south, west, north, east, rows, columns):
    if south >= north:
        raise ValueError('South must be less than north.')
    if west >= east:
        raise ValueError('West must be less than east.')
    if rows <= 0 or columns <= 0:
        raise ValueError('Rows and columns must be positive.')
    latitude_step = (north - south) / rows
    longitude_step = (east - west) / columns

    cells = []
    for row in range(rows):
        cell_south = south + (row * latitude_step)
        cell_north = north if row == rows - 1 else south + ((row + 1) * latitude_step)
        
        for column in range(columns):
            cell_west = west + (column * longitude_step)
            cell_east = east if column == columns - 1 else west + ((column + 1) * longitude_step)

            cells.append({
                'cell_id': create_cell_id(cell_south, cell_west, cell_north, cell_east),
                'south': cell_south,
                'west': cell_west,
                'north': cell_north,
                'east': cell_east
            })
    return cells

def save_grid_geojson(cells, output_file='grid_test.geojson'):
    features = []

    for cell in cells:
        polygon = [
            [cell['west'], cell['south']],
            [cell['east'], cell['south']],
            [cell['east'], cell['north']],
            [cell['west'], cell['north']],
            [cell['west'], cell['south']]
        ]
        features.append({
            'type': 'Feature',
            'properties': {
                'cell_id': cell['cell_id'],
                'south': cell['south'],
                'west': cell['west'],
                'north': cell['north'],
                'east': cell['east']
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': [polygon]
            }
        })

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(geojson, file, indent=2)
    print(f'Saved grid to {output_file}')


class TestGrid(unittest.TestCase):

    def setUp(self):
        self.cells = generate_grid(
            south=14.09,
            west=-87.22,
            north=14.10,
            east=-87.20,
            rows=2,
            columns=2
        )

    def test_creates_four_cells(self):
        self.assertEqual(len(self.cells), 4)

    def test_cell_ids(self):
        expected_ids = [
            'cell_14.090000_-87.220000_14.095000_-87.210000',
            'cell_14.090000_-87.210000_14.095000_-87.200000',
            'cell_14.095000_-87.220000_14.100000_-87.210000',
            'cell_14.095000_-87.210000_14.100000_-87.200000'
        ]
        actual_ids = [cell['cell_id'] for cell in self.cells]
        self.assertEqual(actual_ids, expected_ids)

if __name__ == '__main__':
    preview_cells = generate_grid(
        south=14.09,
        west=-87.22,
        north=14.10,
        east=-87.20,
        rows=2,
        columns=2
    )
    save_grid_geojson(preview_cells)
    unittest.main()