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
import VolunteerHistory from "./components/VolunteerHistory/volunteerHistory";
import VolunteerMatch from "./components/VolunteerMatch/VolunteerMatch";

import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import "./App.css";

function App() {
  return (
    <Router>
      <ToastContainer />
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/register" element={<Registration />} />
          <Route path="/login" element={<Login />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/eventform" element={<Event />} />
          <Route path="/volunteerHistory" element={<VolunteerHistory />} />
          <Route path="/volunteerMatch" element={<VolunteerMatch />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
