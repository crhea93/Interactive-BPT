import matplotlib
matplotlib.use('Agg')  # Set the backend to a non-interactive backend
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from skimage.measure import profile_line
import matplotlib.patches as patches
import cmasher as cmr
import base64
from io import BytesIO
import warnings
warnings.filterwarnings("ignore")

colors = cmr.take_cmap_colors('hsv', 8, return_fmt='hex')
# Create some example data
def clean_flux(data_):
    flux = data_
    return flux

# Read in data
data_Halpha = clean_flux(fits.open('./NGC1275_3_Halpha_mask.fits')[0].data)
data_Halpha_flux = clean_flux(fits.open('./NGC1275_3_Halpha_mask.fits')[0].data)

data_NII = clean_flux(fits.open('./NGC1275_3_NII6583_mask.fits')[0].data)
data_SN3_continuum = fits.open('./NGC1275_3_sinc_continuum.fits')[0].data

NII_Halpha = data_NII/data_Halpha
Eq_width = data_Halpha_flux/data_SN3_continuum
Eq_width_NII = data_NII/data_SN3_continuum

image_paths = ['./NGC1275_lowres_deep.fits', './NGC1275_lowres_3_sinc_Halpha_velocity.fits', './NGC1275_lowres_3_sinc_Halpha_broadening.fits']

front_NIIHalpha = profile_line(np.nan_to_num(NII_Halpha), (48,101), (82,115), linewidth=2, reduce_func=np.sum, mode='reflect')
front_eqwHa = profile_line(np.nan_to_num(Eq_width), (48,101), (82,115), linewidth=2, reduce_func=np.sum, mode='reflect')

scatter_data = [
    {'name': 'Central Region', 'color': colors[0], 'x': np.log10(NII_Halpha[45:115, 75:100].flatten()), 'y': Eq_width[45:115,75:100].flatten()},
    {'name': 'Star Forming Region', 'color': colors[1], 'x': np.log10(NII_Halpha[40:60,20:55].flatten()), 'y': Eq_width[40:60, 20:55].flatten()},
    {'name': 'Horseshoe Knot', 'color': colors[2], 'x': np.log10(NII_Halpha[120:135,135:145].flatten()), 'y': Eq_width[115:130, 135:145].flatten()},
    {'name': 'Small Nothern Bar', 'color': colors[3], 'x': np.log10(NII_Halpha[80:90,140:175].flatten()), 'y': Eq_width[80:90,140:175].flatten()},
    {'name': 'Horseshoe Bottom', 'color': colors[4], 'x': np.log10(NII_Halpha[128:144,124:139].flatten()), 'y': Eq_width[128:144,124:139].flatten()},
    {'name': 'Southern Claw', 'color': colors[5], 'x': np.log10(NII_Halpha[105:140, 15:45].flatten()), 'y': Eq_width[105:130, 15:35].flatten()},
    {'name': 'Large Northern Bar', 'color': colors[6], 'x': np.log10(NII_Halpha[95:115, 140:240].flatten()), 'y': Eq_width[95:110, 140:240].flatten()},
    {'name': 'Shock Front', 'color': colors[7], 'x': np.log10(front_NIIHalpha), 'y': front_eqwHa}
]
binning = 3
region_data = [
    {'name': 'Central Region', 'color': colors[0], 'x': [45,115], 'y': [75,100]},
    {'name': 'Star Forming Region', 'color': colors[1], 'x': [40,60], 'y': [20,55]},
    {'name': 'Horseshoe Knot', 'color': colors[2], 'x': [115,130], 'y': [135,145]},
    {'name': 'Small Nothern Bar', 'color': colors[3], 'x': [80, 90], 'y': [140,175]},
    {'name': 'Horseshoe Bottom', 'color': colors[4], 'x': [128,144], 'y': [124,139]},
    {'name': 'Southern Claw', 'color': colors[5], 'x': [105,130], 'y': [15,35]},
    {'name': 'Large Northern Bar', 'color': colors[6], 'x': [95,110], 'y': [140,240]},
    {'name': 'Shock Front', 'color': colors[7], 'x':[48, 82] , 'y': [101, 115]}
]

# Initialize the Dash app
app = dash.Dash(__name__)

image_data = fits.open('NGC1275_lowres_deep.fits')[0].data[200:1000, 1000:1600]
image_data = np.arcsinh(image_data)

app.layout = html.Div([
    html.Div([
        dcc.Graph(id='scatter-plot', config={'displayModeBar': False}),
    ], style={'width': '60%', 'display': 'inline-block', 'vertical-align': 'middle'}),
    html.Div([
        html.Img(id='image-display', width='100%', height='auto'),
        dcc.Checklist(
            id='plot-selector',
            options=[
                {'label': scatter['name'], 'value': scatter['name']} for scatter in scatter_data
            ],
            value=[scatter['name'] for scatter in scatter_data],
            style={'margin-top': '10px'}
        ),
        dcc.Dropdown(
            id='image-dropdown',
            options=[
                {'label': 'Deep Image', 'value': 0},
                {'label': 'Velocity', 'value': 1},
                {'label': 'Broadening', 'value': 2},
                # Add more options for additional images
            ],
            value=0,
            style={'margin-top': '10px'}
        )
    ], style={'width': '20%', 'display': 'inline-block', 'padding': '20px', 'vertical-align': 'middle'})
], style={'text-align': 'center'})
# Define the callback function to update the scatter plot
@app.callback(
    [Output('scatter-plot', 'figure'), Output('image-display', 'src'), Output('image-display', 'style')],
    [Input('plot-selector', 'value'), Input('image-dropdown', 'value'), Input('scatter-plot', 'hoverData')]
    #[Output('scatter-plot', 'figure'), Output('image-display', 'style')],
    #[Input('plot-selector', 'value'), Input('scatter-plot', 'hoverData')]
)

def update_scatter_plot(selected_plots, selected_image, hover_data):
#def update_scatter_plot(selected_plots, hover_data):
    data = []
    rectangles = []
    for scatter, region in zip(scatter_data, region_data):
        if scatter['name'] in selected_plots:
            scatter_trace = go.Scatter(
                x=scatter['x'],
                y=scatter['y'],
                mode='markers',
                marker=dict(size=10, opacity=0.5, color=scatter['color']),
                name=scatter['name'], 
            )
            data.append(scatter_trace)
            # Add rectangles for the selected scatter plot
            x_min = 3*min(region['x'])
            x_max = 3*max(region['x'])
            y_min = 3*min(region['y'])
            y_max = 3*max(region['y'])
            rect = patches.Rectangle(
               (x_min, y_min), x_max - x_min, y_max - y_min,
               linewidth=2, edgecolor=scatter['color'], facecolor='none'
           )
            rectangles.append(rect)
    layout = go.Layout(
        #title='Equivalent Width BPT Map',
        title=dict(text="Equivalent Width BPT Map", font=dict(size=30), automargin=True, yref='paper'),
        xaxis=dict(title='Log(<i>[NII]</i>/Hα)', tickformat='latex', showgrid=False, zeroline=False),
        yaxis=dict(title='W<sub>Hα</sub> [Å]', tickformat='latex', type='log', showgrid=False, zeroline=False, dtick=1, showexponent= 'all', exponentformat= 'e'),
        xaxis_range=[-1, 1],  # Set your desired x-axis limits
        yaxis_range=[-1, 4],  # Set your desired y-axis limits
        width=1000,  # Set width to ensure square aspect ratio
        height=800,  # Set height to ensure square aspect ratio
        #margin=dict(l=40, r=40, b=40, t=60),  # Adjust plot margins
        shapes=[
            # Vertical line extending across visible y-axis range
            {'type': 'line', 'x0': -0.4, 'x1': -0.4, 'y0': -.1, 'y1': 1000, 'line': {'color': 'black', 'width': 1}},
            # Horizontal line extending across visible y-axis range
            {'type': 'line', 'x0': -1, 'x1': 1, 'y0': 6, 'y1': 6, 'line': {'color': 'black', 'width': 1}},
            # Dashed horizontal line extending across visible y-axis range
            {'type': 'line', 'x0': -1, 'x1': 1, 'y0': 0.05, 'y1': 0.05, 'line': {'color': 'black', 'width': 1, 'dash': 'dash'}},
            # Sloped dashed line
            #{'type': 'line', 'x0': -1, 'x1': 0.75, 'y0': np.exp(-2.35 * -1 + np.log(0.05)), 'y1': np.exp(-2.35 * 0.75 + np.log(0.05)), 'line': {'color': 'black', 'width': 1, 'dash': 'dash'}}
        ],
        annotations=[
            {'x': -0.8, 'y': 2, 'xref': 'x', 'yref': 'y', 'text': '<b>SF</b>', 'showarrow': False, 'font': {'size': 24}},
            {'x': 0.3, 'y': 2, 'xref': 'x', 'yref': 'y', 'text': '<b>Seyferts</b>', 'showarrow': False, 'font': {'size': 24}},
            {'x': 0.3, 'y': 0.25, 'xref': 'x', 'yref': 'y', 'text': '<b>LINERs</b>', 'showarrow': False, 'font': {'size': 24}},
        ]
    )
    # Convert FITS image data to an image format (e.g., PNG) using matplotlib
    fig, ax = plt.subplots(figsize=(8, 8))
    # Read the selected image data using astropy
    # selected_image_path = image_paths[selected_image]
    selected_image_path = 'NGC1275_lowres_deep.fits'
    
    selected_image_data = fits.open(selected_image_path)[0].data[200:1000, 1000:1600]
    selected_image_data = np.arcsinh(selected_image_data)
    #if selected_image == 0:
    #    selected_image_data = fits.open(selected_image_path)[0].data[200:1000, 1000:1500]
    #    selected_image_data = np.arcsinh(selected_image_data)
    #else:
    #    selected_image_data = fits.open(selected_image_path)[0].data
    #    selected_image_data = selected_image_data

    #ax.imshow(selected_image_data, cmap='magma', origin='lower', vmin=np.nanpercentile(selected_image_data, 5), vmax=np.nanpercentile(selected_image_data, 99.5))
    ax.imshow(selected_image_data, cmap='magma', origin='lower', vmin=np.nanpercentile(image_data, 5), vmax=np.nanpercentile(image_data, 99))  # Display the FITS image data as grayscale

    for rect in rectangles:
        ax.add_patch(rect)

    ax.axis('off')  # Turn off axis
    # Highlight the hovered pixel if available
    hover_style = {}
    #print(hover_data['points'][0]['x'])
    # if hover_data is not None:
    #     x_hover = hover_data['points'][0]['x']
    #     y_hover = hover_data['points'][0]['y']
    #     hover_style = {
    #         'position': 'absolute',
    #         'left': f'{x_hover * 100}%',  # Convert normalized coordinates to percentage
    #         'top': f'{(1 - y_hover) * 100}%',  # Convert normalized coordinates to percentage
    #         'width': '10px',
    #         'height': '10px',
    #         'border': '2px solid red',
    #         'box-sizing': 'border-box',
    #     }

    # Save the converted image to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()

    # Get the base64-encoded image data
    buf.seek(0)
    image_data_base64 = base64.b64encode(buf.read()).decode()




    return {'data': data, 'layout': layout}, 'data:image/png;base64,{}'.format(image_data_base64), hover_style




# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
