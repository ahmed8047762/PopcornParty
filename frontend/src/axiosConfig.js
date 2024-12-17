import axios from 'axios';

// Create a custom instance of axios
const axiosInstance = axios.create();

// Add a request interceptor
axiosInstance.interceptors.request.use(
    config => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// Add a response interceptor
axiosInstance.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;

        // If the error status is 401 and there is no originalRequest._retry flag,
        // it means the token has expired and we need to refresh it
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                const response = await axios.post('http://127.0.0.1:8000/api/accounts/token/refresh/', {
                    refresh: refreshToken
                });

                const { access } = response.data;

                // Store the new token
                localStorage.setItem('access_token', access);

                // Update the authorization header
                originalRequest.headers.Authorization = `Bearer ${access}`;

                // Retry the original request
                return axiosInstance(originalRequest);
            } catch (error) {
                // If refresh token fails, redirect to login
                localStorage.clear();
                window.location.href = '/login';
                return Promise.reject(error);
            }
        }

        return Promise.reject(error);
    }
);

export default axiosInstance;
