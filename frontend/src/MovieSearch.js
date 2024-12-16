import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './MovieSearch.css';

const MovieSearch = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [recentMovies, setRecentMovies] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingRecent, setIsLoadingRecent] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            alert('Please log in to search movies');
            navigate('/login');
            return;
        }
        fetchRecentMovies();
    }, [navigate]);

    const getAuthHeaders = () => {
        const accessToken = localStorage.getItem('access_token');
        return {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            }
        };
    };

    const fetchRecentMovies = async () => {
        try {
            const response = await axios.get(
                'http://127.0.0.1:8000/api/movies/search/',
                getAuthHeaders()
            );
            setRecentMovies(response.data);
        } catch (error) {
            console.error('Error fetching recent movies:', error);
            if (error.response?.status === 401) {
                alert('Please log in to view movies');
                navigate('/login');
            }
        } finally {
            setIsLoadingRecent(false);
        }
    };

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        setIsLoading(true);
        try {
            const response = await axios.get(
                `http://127.0.0.1:8000/api/movies/omdb/?title=${encodeURIComponent(searchQuery)}`,
                getAuthHeaders()
            );
            setSearchResults(response.data);
            fetchRecentMovies();
        } catch (error) {
            console.error('Error searching movies:', error);
            if (error.response?.status === 401) {
                alert('Please log in to search movies');
                navigate('/login');
            } else {
                alert('Error searching movies. Please try again.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreateEvent = async (movie) => {
        const accessToken = localStorage.getItem('access_token');
        
        if (!accessToken) {
            alert('Please log in to create events');
            navigate('/login');
            return;
        }

        try {
            navigate('/create-event', { state: { movie } });
        } catch (error) {
            console.error('Error creating event:', error);
            alert('Error creating event. Please try again.');
        }
    };

    const MovieCard = ({ movie }) => (
        <div className="movie-card">
            <img
                src={movie.poster || movie.poster_url || 'https://via.placeholder.com/150x225?text=No+Poster'}
                alt={movie.title}
                className="movie-poster"
                onError={(e) => {
                    e.target.src = 'https://via.placeholder.com/150x225?text=No+Poster';
                }}
            />
            <div className="movie-info">
                <h3>{movie.title}</h3>
                <p className="movie-description">{movie.description}</p>
                <p>Release Date: {new Date(movie.release_date).toLocaleDateString()}</p>
                <button
                    onClick={() => handleCreateEvent(movie)}
                    className="create-event-button"
                >
                    Create Event
                </button>
            </div>
        </div>
    );

    return (
        <div className="movie-search-container">
            <form onSubmit={handleSearch} className="search-form">
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Enter movie title..."
                    className="search-input"
                />
                <button type="submit" className="search-button" disabled={isLoading}>
                    {isLoading ? 'Searching...' : 'Search'}
                </button>
            </form>

            {searchResults.length > 0 && (
                <div className="search-results-section">
                    <h2>Search Results</h2>
                    <div className="movie-grid">
                        {searchResults.map((movie, index) => (
                            <MovieCard key={`search-${movie.id || index}`} movie={movie} />
                        ))}
                    </div>
                </div>
            )}

            <div className="recent-movies-section">
                <h2>Recently Searched Movies</h2>
                {isLoadingRecent ? (
                    <div className="loading">Loading recent movies...</div>
                ) : recentMovies.length > 0 ? (
                    <div className="movie-grid">
                        {recentMovies.map((movie, index) => (
                            <MovieCard key={`recent-${movie.id}`} movie={movie} />
                        ))}
                    </div>
                ) : (
                    <div className="no-movies">No movies have been searched yet.</div>
                )}
            </div>
        </div>
    );
};

export default MovieSearch;
