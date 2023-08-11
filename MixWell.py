import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

def get_spotify_track_info(track_name):
    configure()
    # Initialize the Spotify API client
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Search for the track
    results = sp.search(q=track_name, type='track', limit=1)

    if not results or not results['tracks']['items']:
        raise ValueError("Track not found.")

    track = results['tracks']['items'][0]
    track_name = track['name']
    artists = ", ".join([artist['name'] for artist in track['artists']])
    track_id = track['id']
    artist_id = track['artists'][0]['id']
    artist_genres = sp.artist(artist_id)['genres']
    genres = ", ".join(set(artist_genres))

    # Get audio features for the track
    audio_features = sp.audio_features(track_id)[0]

    # Extract relevant information
    bpm = audio_features['tempo']
    key = audio_features['key']
    energy = audio_features['energy']

    # Return the track name, artists, BPM, key, energy level, and artist ID
    return track_name, artists, bpm, key, energy, artist_id, genres

# Function to get recommended tracks based on the current track's information
def get_recommended_tracks(bpm, key, energy, artist_id):
    configure()
    # Initialize the Spotify API client
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    try:
        # Use Spotify's recommendations endpoint to get recommended tracks
        recommendations = sp.recommendations(seed_artists=[artist_id], target_energy=energy, target_tempo=bpm, target_key=key, limit=20)

        # Extract track names and artists from the recommendations
        recommended_tracks = []
        for track in recommendations['tracks']:
            track_name = track['name']
            artists = ", ".join([artist['name'] for artist in track['artists']])
            recommended_tracks.append(f"{track_name} by {artists}")

        return recommended_tracks
    
    # Exception handling
    except spotipy.exceptions.SpotifyException as e:
        print(f"SpotifyException: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

# Function to handle the "Search" button click
def search_button_clicked():
    song_name = entry.get()
    if not song_name:
        messagebox.showwarning("Warning", "Please enter a song name.")
    else:
        try:
            # Get the information from Spotify API
            track_name, artists, bpm, key, energy, artist_id, genres = get_spotify_track_info(song_name)
            
            # Convert numerical expression into lettered expression for notes
            notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            key_note = notes[key]
            
            # Update the label with the track information
            result_label.config(text=f"Track: {track_name} by {artists}\nBPM: {bpm}\nKey: {key_note}\nEnergy: {energy}\nGenres: {genres}")

            # Fetch and display recommended tracks
            recommended_tracks = get_recommended_tracks(bpm, key, energy, artist_id)

            # Clear the previous recommendations
            recommended_text.config(state=tk.NORMAL)
            recommended_text.delete("1.0", tk.END)

            # Display the recommended tracks with numbers
            if recommended_tracks:
                for i, track in enumerate(recommended_tracks, 1):
                    recommended_text.insert(tk.END, f"{i}. {track}\n")
            else:
                recommended_text.insert(tk.END, "No recommended tracks found.\n")

            recommended_text.config(state=tk.DISABLED)  # Make the text widget read-only

        # Some exception handling
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            


# Create the main application window
app = tk.Tk()
app.title("MixWell")
app.geometry("750x450")
app.configure(bg="#FFFFFF") 

# font for the application
custom_font = ("Arial", 12)

# Create and style the widgets with color and font
frame = ttk.Frame(app, padding=20)
frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

entry_label = ttk.Label(frame, text="Enter the name of a song:", font=custom_font, anchor="e", foreground="#333333")
entry_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

entry = ttk.Entry(frame, width=40, font=custom_font)
entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

search_button = ttk.Button(frame, text="Search", command=search_button_clicked, cursor="hand2", style="Custom.TButton")
search_button.grid(row=0, column=2, padx=5, pady=5)

result_label = ttk.Label(frame, text="", font=custom_font, wraplength=400, justify="left", foreground="#333333")
result_label.grid(row=1, column=0, columnspan=3, padx=5, pady=10)

recommended_label = ttk.Label(frame, text="Recommended tracks:", font=custom_font, anchor="w", foreground="#333333")
recommended_label.grid(row=2, column=0, padx=5, pady=5, columnspan=3, sticky="w")

recommended_text = tk.Text(frame, width=60, height=10, font=custom_font, wrap="word", state=tk.DISABLED, bg="#F5F5F5", bd=0)
recommended_text.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

# Apply custom styles for the widgets
style = ttk.Style(app)
style.theme_use("clam")
style.configure("Custom.TButton", font=custom_font, background="#1DB954", foreground="white", padding=5, width=10)

# Configure column and row weights to allow proper resizing
frame.columnconfigure(1, weight=1)
frame.rowconfigure(3, weight=1)

# Run the application
app.mainloop()
