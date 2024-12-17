// src/Home.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const Home = () => {
    const [events, setEvents] = useState([]);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [userEmail, setUserEmail] = useState(null);

    useEffect(() => {
        const accessToken = localStorage.getItem('access_token');
        const email = localStorage.getItem('user_email');
        console.log('User email from localStorage:', email);
        setIsAuthenticated(!!accessToken);
        setUserEmail(email);

        // Fetch events from the public endpoint
        axios.get('http://127.0.0.1:8000/api/events/public/', {
            headers: {
                'Content-Type': 'application/json',
                ...(accessToken && { 'Authorization': `Bearer ${accessToken}` })
            }
        })
        .then(response => {
            console.log('Events response:', response.data);
            setEvents(response.data);
            setError(null);
        })
        .catch(error => {
            console.error('Error fetching events:', error);
            setError('Failed to load events. Please try again later.');
            // Clear events to show empty state
            setEvents([]);
        });
    }, [navigate]);

    const handleJoinRequest = async (eventId) => {
        if (!isAuthenticated) {
            alert('Please log in to join events');
            navigate('/login');
            return;
        }

        const accessToken = localStorage.getItem('access_token');
    
        try {
            const response = await axios.post(
                'http://127.0.0.1:8000/api/notifications/join-request/',
                { event_id: eventId },
                {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json',
                    }
                }
            );
    
            // Check for both 200 and 201 status codes
            if (response.status === 200 || response.status === 201) {
                alert(response.data.message || 'Join request sent successfully!');
            }
        } catch (error) {
            console.error('Error sending join request:', error);
            if (error.response) {
                if (error.response.status === 401) {
                    alert('Please log in again to continue');
                    localStorage.clear();
                    setIsAuthenticated(false);
                    navigate('/login');
                } else {
                    // Show the specific error message from the backend
                    alert(error.response.data.error || 'Failed to send join request');
                }
            } else {
                alert('Failed to send join request. Please try again.');
            }
        }
    };

    const handleInvite = (eventId) => {
        navigate(`/invite/${eventId}`);
    };

    const isEventHost = (event) => {
        console.log('Comparing emails - Event host:', event.host_email, 'User:', userEmail);
        return event.host_email === userEmail;
    };

    return (
        <div className="home-container">
            <h2>Available Events</h2>
            {error && <div className="alert alert-danger">{error}</div>}
            {events.length === 0 ? (
                <p>No events available. {isAuthenticated ? 'Why not create one?' : 'Please check back later!'}</p>
            ) : (
                <div className="events-grid">
                    {events.map(event => {
                        console.log('Event:', event);
                        const isHost = isEventHost(event);
                        console.log('Is host?', isHost);
                        return (
                            <div key={event.id} className="event-card">
                                <img 
                                    src={event.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster'} 
                                    alt={event.title || 'Movie poster'} 
                                    className="event-poster"
                                />
                                <div className="event-info">
                                    <h3>{event.title}</h3>
                                    <p>{event.description}</p>
                                    <p><strong>Date:</strong> {new Date(event.date).toLocaleString()}</p>
                                    <p><strong>Location:</strong> {event.location}</p>
                                    <p><strong>Host:</strong> {event.host_email || 'Anonymous'}</p>
                                    <div className="event-actions">
                                        {isAuthenticated && (
                                            isHost ? (
                                                <button 
                                                    onClick={() => handleInvite(event.id)}
                                                    className="btn btn-secondary"
                                                >
                                                    Invite Someone
                                                </button>
                                            ) : (
                                                <button 
                                                    onClick={() => handleJoinRequest(event.id)}
                                                    className="btn btn-primary"
                                                >
                                                    Join Event
                                                </button>
                                            )
                                        )}
                                        {!isAuthenticated && (
                                            <button 
                                                onClick={() => navigate('/login')}
                                                className="btn btn-primary"
                                            >
                                                Login to Join
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default Home;