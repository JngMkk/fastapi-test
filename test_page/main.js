const apiBaseURL = 'https://127.0.0.1:8000/api/v1';
let accessToken = '';

function signupUser() {
    const userData = {
        email: document.getElementById('signupEmail').value,
        password: document.getElementById('signupPassword').value
    };
    axios.post(`${apiBaseURL}/users/signup`, userData)
        .then(response => alert('Signup Success'))
        .catch(error => alert('Signup Error: ' + error.response.data.message));
}

function signinUser() {
    const credentials = {
        email: document.getElementById('signinEmail').value,
        password: document.getElementById('signinPassword').value
    };
    axios.post(`${apiBaseURL}/users/signin`, credentials)
        .then(response => {
            alert('Signin Success');
            accessToken = response.data.access_token;
        })
        .catch(error => alert('Signin Error: ' + error.response.data.message));
}

function signoutUser() {
    makeAuthorizedRequest('post', `${apiBaseURL}/users/signout`)
        .then(response => {
            alert('Signout Success');
            accessToken = '';
        })
        .catch(error => alert('Signout Error: ' + error.response.data.message));
}

function createEvent() {
    const eventData = {
        name: document.getElementById('eventName').value,
        description: document.getElementById('eventDescription').value
    };
    makeAuthorizedRequest('post', `${apiBaseURL}/events`, eventData)
        .then(response => alert('Event Created'))
        .catch(error => alert('Create Event Error: ' + error.response.data.message));
}

function getAllEvents() {
    makeAuthorizedRequest('get', `${apiBaseURL}/events`)
        .then(response => console.log(response.data))
        .catch(error => alert('Get Events Error: ' + error.response.data.message));
}

function getEventById() {
    const eventId = document.getElementById('eventId').value;
    makeAuthorizedRequest('get', `${apiBaseURL}/events/${eventId}`)
        .then(response => console.log(response.data))
        .catch(error => alert('Get Event Error: ' + error.response.data.message));
}

function updateEvent() {
    const eventId = document.getElementById('updateEventId').value;
    const updateData = {
        name: document.getElementById('updateEventName').value,
        description: document.getElementById('updateEventDescription').value
    };
    makeAuthorizedRequest('put', `${apiBaseURL}/events/${eventId}`, updateData)
        .then(response => alert('Event Updated'))
        .catch(error => alert('Update Event Error: ' + error.response.data.message));
}

function deleteEvent() {
    const eventId = document.getElementById('deleteEventId').value;
    makeAuthorizedRequest('delete', `${apiBaseURL}/events/${eventId}`)
        .then(response => alert('Event Deleted'))
        .catch(error => alert('Delete Event Error: ' + error.response.data.message));
}

function makeAuthorizedRequest(method, url, data = null) {
    return axios({
        method: method,
        url: url,
        data: data,
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    }).catch(error => {
        if (error.response && error.response.status === 401 && error.response.data.detail === "Invalid Token.") {
            return refreshAccessToken().then(newToken => {
                accessToken = newToken;
                return axios({
                    method: method,
                    url: url,
                    data: data,
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
            });
        } else {
            throw error;
        }
    });
}

function refreshAccessToken() {
    return axios.post(`${apiBaseURL}/users/refresh`)
        .then(response => {
            alert('Token Refreshed');
            return response.data.access_token;
        })
        .catch(error => {
            alert('Refresh Token Error: ' + error.response.data.message);
            throw error;
        });
}