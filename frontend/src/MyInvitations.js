import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosInstance from './axiosConfig';
import './MyInvitations.css';

const MyInvitations = () => {
    const [pendingInvitations, setPendingInvitations] = useState([]);
    const [acceptedEvents, setAcceptedEvents] = useState([]);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            navigate('/login');
            return;
        }

        // Fetch invitations
        axiosInstance.get('http://127.0.0.1:8000/api/events/invitations/')
            .then(response => {
                const pending = response.data.filter(inv => inv.status === 'pending');
                const accepted = response.data.filter(inv => inv.status === 'accepted');
                setPendingInvitations(pending);
                setAcceptedEvents(accepted);
            })
            .catch(error => {
                console.error('Error fetching invitations:', error);
                if (error.response && error.response.status === 401) {
                    navigate('/login');
                } else {
                    setError('Failed to load invitations');
                }
            });
    }, [navigate]);

    const handleResponse = async (invitationId, status) => {
        try {
            await axiosInstance.put(
                `http://127.0.0.1:8000/api/events/invitations/${invitationId}/rsvp/`,
                { status }
            );
            // Refresh the invitations list after successful response
            const response = await axiosInstance.get('http://127.0.0.1:8000/api/events/invitations/');
            const pending = response.data.filter(inv => inv.status === 'pending');
            const accepted = response.data.filter(inv => inv.status === 'accepted');
            setPendingInvitations(pending);
            setAcceptedEvents(accepted);
        } catch (error) {
            console.error('Error responding to invitation:', error);
            if (error.response && error.response.status === 401) {
                navigate('/login');
            } else {
                setError('Failed to respond to invitation: ' + 
                    (error.response?.data?.error || error.message || 'Unknown error'));
            }
        }
    };

    return (
        <div className="invitations-container">
            <h2>My Invitations</h2>
            
            {error && <div className="alert alert-danger">{error}</div>}
            
            <div className="section">
                <h3>Pending Invitations</h3>
                {pendingInvitations.length === 0 ? (
                    <p>No pending invitations</p>
                ) : (
                    <div className="invitations-grid">
                        {pendingInvitations.map(invitation => (
                            <div key={invitation.id} className="invitation-card">
                                <img 
                                    src={invitation.event.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster'} 
                                    alt={invitation.event.title} 
                                    className="event-poster"
                                />
                                <div className="invitation-details">
                                    <h4>{invitation.event.title}</h4>
                                    <p><strong>Date:</strong> {new Date(invitation.event.date).toLocaleString()}</p>
                                    <p><strong>Location:</strong> {invitation.event.location}</p>
                                    <p><strong>Host:</strong> {invitation.event.host_email}</p>
                                    <div className="invitation-actions">
                                        <button 
                                            onClick={() => handleResponse(invitation.id, 'accepted')}
                                            className="btn btn-success"
                                        >
                                            Accept
                                        </button>
                                        <button 
                                            onClick={() => handleResponse(invitation.id, 'declined')}
                                            className="btn btn-danger"
                                        >
                                            Decline
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="section">
                <h3>Accepted Events</h3>
                {acceptedEvents.length === 0 ? (
                    <p>No accepted events</p>
                ) : (
                    <div className="events-grid">
                        {acceptedEvents.map(invitation => (
                            <div key={invitation.id} className="event-card">
                                <img 
                                    src={invitation.event.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster'} 
                                    alt={invitation.event.title} 
                                    className="event-poster"
                                />
                                <div className="event-details">
                                    <h4>{invitation.event.title}</h4>
                                    <p><strong>Date:</strong> {new Date(invitation.event.date).toLocaleString()}</p>
                                    <p><strong>Location:</strong> {invitation.event.location}</p>
                                    <p><strong>Host:</strong> {invitation.event.host_email}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <button onClick={() => navigate('/')} className="btn btn-secondary mt-3">
                Back to Events
            </button>
        </div>
    );
};

export default MyInvitations;
