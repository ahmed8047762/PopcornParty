// src/Home.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Home = () => {
    const [events, setEvents] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        // Fetch events from the Django API
        axios.get('http://127.0.0.1:8000/api/events/')
            .then(response => {
                setEvents(response.data);
            })
            .catch(error => {
                console.error('Error fetching events:', error);
            });
    }, []);

    const handleJoinRequest = async (eventId) => {
        const accessToken = localStorage.getItem('access_token');
        
        if (!accessToken) {
            alert('Please log in to join events');
            navigate('/login');
            return;
        }
    
        try {
            const response = await axios.post(
                'http://127.0.0.1:8000/api/notifications/join-request/',
                { event_id: eventId },  // Only send event_id
                {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json',
                    }
                }
            );
    
            if (response.status === 200) {
                alert(response.data.message || 'Join request sent successfully!');
            }
        } catch (error) {
            console.error('Error sending join request:', error);
            if (error.response) {
                if (error.response.status === 401) {
                    alert('Please log in again to continue');
                    localStorage.clear();
                    navigate('/login');
                } else {
                    // Show the specific error message from the backend
                    alert(error.response.data.error || error.response.data.message || 'Failed to send join request');
                }
            } else {
                alert('Failed to send join request: Network error');
            }
        }
    };

    return (
        <div className="container">
            <h1 className="mt-4">Available Events</h1>
            <div className="list-group">
                {events.map(event => (
                    <div key={event.id} className="list-group-item">
                        <h5>{event.title}</h5>
                        <p>{event.description}</p>
                        <button 
                            className="btn btn-primary" 
                            onClick={() => handleJoinRequest(event.id)}>
                            Request to Join
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Home;