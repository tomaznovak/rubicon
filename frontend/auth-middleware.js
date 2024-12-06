class AuthMiddleware {
    constructor() {
        this.isRefreshing = false;
        this.failedQueue = [];
    }

    processQueue(error, token = null) {
        this.failedQueue.forEach(prom => {
            if (error) {
                prom.reject(error);
            } else {
                prom.resolve(token);
            }
        });
        this.failedQueue = [];
    }

    setupInterceptor() {
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const [url, config = {}] = args;

            const accessToken = localStorage.getItem('access_token');
            if (accessToken) {
                config.headers = {
                ...config.headers,
                'Authorization': `Bearer ${accessToken}`
                };
            }

            try {
                const response = await originalFetch(url, config);

                if (response.status === 401) {
                    if (!this.isRefreshing) {
                        this.isRefreshing = true;
                        try {
                            const newToken = await this.refreshToken();
                            this.isRefreshing = false;
                            this.processQueue(null, newToken);

                            config.headers['Authorization'] = `Bearer ${newToken}`;
                            return originalFetch(url, config);
                        } catch (error) {
                            this.isRefreshing = false;
                            this.processQueue(error, null);
                            this.handleAuthError();
                            throw error;
                        }
                    } else {
                        return new Promise((resolve, reject) => {
                            this.failedQueue.push({ resolve, reject});
                        })
                            .then(token => {
                                config.headers['Authorization'] = `Bearer ${token}`;
                                return originalFetch(url, config);
                            })
                            .catch(err => {
                                throw err;
                            });
                    }
                }
                return response;

            } catch (error) {
                throw error;
            }
        };
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }
        try {
            const response = await fetch('/refresh', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${refreshToken}`
                }
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            return data.accessToken;
        } catch (error) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            throw error;
        }
    }

    handleAuthError() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
    }
}

const AuthMiddleware = new AuthMiddleware();
AuthMiddleware.setupInterceptor();