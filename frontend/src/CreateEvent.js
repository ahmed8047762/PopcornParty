import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './CreateEvent.css';

const CreateEvent = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const movie = location.state?.movie;
    const [eventData, setEventData] = useState({
        title: `Watch ${movie?.title || ''}`,
        description: '',
        date: '',
        time: '',
        location: '',
        movie: movie?.id,
    });
    const [inviteeEmail, setInviteeEmail] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [error, setError] = useState('');

    if (!movie) {
        navigate('/movies');
        return null;
    }

    const handleCreateEvent = async (e) => {
        e.preventDefault();
        setIsCreating(true);
        setError('');

        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            navigate('/login');
            return;
        }

        try {
            // Create the event
            console.log('Creating event with data:', {
                title: eventData.title,
                description: eventData.description,
                date: `${eventData.date}T${eventData.time}:00Z`,
                location: eventData.location,
                movie: eventData.movie,
                invitee_email: inviteeEmail // Add invitee email to event creation
            });

            const response = await axios.post(
                'http://127.0.0.1:8000/api/events/',
                {
                    title: eventData.title,
                    description: eventData.description,
                    date: `${eventData.date}T${eventData.time}:00Z`,
                    location: eventData.location,
                    movie: eventData.movie,
                    invitee_email: inviteeEmail // Add invitee email to event creation
                },
                {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json',
                    }
                }
            );

            console.log('Event creation response:', response);
            navigate('/');
        } catch (error) {
            console.error('Error creating event:', error);
            console.error('Error response data:', error.response?.data);
            
            setError(error.response?.data?.message || 'Error creating event. Please check all fields are filled correctly.');
        } finally {
            setIsCreating(false);
        }
    };

    return (
        <div className="create-event-container">
            <div className="movie-preview">
                <img
                    src={movie.poster || movie.poster_url}
                    alt={movie.title}
                    className="movie-poster"
                    onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/150x225?text=No+Poster';
                    }}
                />
                <div className="movie-details">
                    <h2>{movie.title}</h2>
                    <p>{movie.description}</p>
                </div>
            </div>

            <form onSubmit={handleCreateEvent} className="event-form">
                <h3>Create Event</h3>
                
                <div className="form-group">
                    <label>Event Title</label>
                    <input
                        type="text"
                        value={eventData.title}
                        onChange={(e) => setEventData({...eventData, title: e.target.value})}
                        required
                        className="form-control"
                    />
                </div>

                <div className="form-group">
                    <label>Description</label>
                    <textarea
                        value={eventData.description}
                        onChange={(e) => setEventData({...eventData, description: e.target.value})}
                        className="form-control"
                        rows="3"
                    />
                </div>

                <div className="form-group">
                    <label>Location</label>
                    <input
                        type="text"
                        value={eventData.location}
                        onChange={(e) => setEventData({...eventData, location: e.target.value})}
                        required
                        placeholder="Enter event location"
                        className="form-control"
                    />
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label>Date</label>
                        <input
                            type="date"
                            value={eventData.date}
                            onChange={(e) => setEventData({...eventData, date: e.target.value})}
                            required
                            className="form-control"
                        />
                    </div>

                    <div className="form-group">
                        <label>Time</label>
                        <input
                            type="time"
                            value={eventData.time}
                            onChange={(e) => setEventData({...eventData, time: e.target.value})}
                            required
                            className="form-control"
                        />
                    </div>
                </div>

                <div className="form-group">
                    <label>Invite User (Email)</label>
                    <input
                        type="email"
                        value={inviteeEmail}
                        onChange={(e) => setInviteeEmail(e.target.value)}
                        placeholder="Enter email to invite"
                        className="form-control"
                    />
                </div>

                {error && <div className="alert alert-danger">{error}</div>}

                <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={isCreating}
                >
                    {isCreating ? 'Creating...' : 'Create Event'}
                </button>
            </form>
        </div>
    );
};

export default CreateEvent;
