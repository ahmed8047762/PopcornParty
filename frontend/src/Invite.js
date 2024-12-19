import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import './Invite.css';

const Invite = () => {
    const [event, setEvent] = useState(null);
    const [email, setEmail] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const { eventId } = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            navigate('/login');
            return;
        }

        // Fetch event details
        axios.get(`http://127.0.0.1:8000/api/events/${eventId}/`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            setEvent(response.data);
            if (response.data.host_email !== localStorage.getItem('user_email')) {
                setError('You are not authorized to invite people to this event');
                setTimeout(() => navigate('/'), 3000);
            }
        })
        .catch(error => {
            console.error('Error fetching event:', error);
            setError('Failed to load event details');
        });
    }, [eventId, navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            navigate('/login');
            return;
        }

        // Split email string by commas and trim whitespace
        const emails = email.split(',').map(email => email.trim()).filter(email => email);

        try {
            // Send invitations for each email
            const promises = emails.map(async (singleEmail) => {
                return axios.post(
                    `http://127.0.0.1:8000/api/events/${eventId}/invite/`,
                    {
                        email: singleEmail
                    },
                    {
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                            'Content-Type': 'application/json',
                        }
                    }
                );
            });

            // Wait for all invitations to be sent
            await Promise.all(promises);
            setSuccess('Invitations sent successfully!');
            setEmail('');
        } catch (error) {
            console.error('Error sending invitation:', error);
            console.error('Error response:', error.response?.data);
            
            if (error.response) {
                if (error.response.status === 401) {
                    alert('Please log in again to continue');
                    localStorage.clear();
                    navigate('/login');
                } else {
                    // Show the specific error message from the backend
                    const errorMessage = error.response.data.error || 
                                      error.response.data.email || 
                                      'Failed to send invitation';
                    setError(errorMessage);
                }
            } else {
                setError('Failed to send invitation. Please try again.');
            }
        }
    };

    if (!event) {
        return <div className="loading">Loading...</div>;
    }

    return (
        <div className="invite-container">
            <h2>Invite to Event: {event.title}</h2>
            <div className="event-details">
                <img 
                    src={event.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster'} 
                    alt={event.title} 
                    className="event-poster"
                />
                <div className="event-info">
                    <p><strong>Date:</strong> {new Date(event.date).toLocaleString()}</p>
                    <p><strong>Location:</strong> {event.location}</p>
                    <p><strong>Description:</strong> {event.description}</p>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="invite-form">
                <div className="form-group">
                    <label htmlFor="email">Invite by Email:</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter email address(es), separated by commas"
                        required
                        className="form-control"
                    />
                </div>
                <button type="submit" className="btn btn-primary">Send Invitation</button>
            </form>

            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <button onClick={() => navigate('/')} className="btn btn-secondary mt-3">
                Back to Events
            </button>
        </div>
    );
};

export default Invite;
