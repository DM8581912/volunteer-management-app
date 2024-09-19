import React from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import Registration from "./components/Registration/Registration";
import Login from "./components/Login/Login";
import Profile from "./components/Profile/Profile";
import Event from "./components/EventForm/Event";
import "./App.css";
import VolunteerHistory from "./components/VolunteerHistory/volunteerHistory";

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Default route to redirect to Login */}
          <Route path="/" element={<Navigate to="/login" />} />

          {/* Other routes */}
          <Route path="/register" element={<Registration />} />
          <Route path="/login" element={<Login />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/eventform" element={<Event />} />
          <Route path="/volunteerHistory" element={<VolunteerHistory />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
