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

import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import "./App.css";

const newEvent = () => {
  toast.success("created new event!");
};
const newUpdate = () => {
  toast.info("there's an update!");
};
const newAssignment = () => {
  toast.info("there's a new assignment!");
};

function App() {
  return (
    <Router>
      {/* Temp container
        Implementation would come when database is implemented to change on data
      */}
      <div className="toast-container">
        <button onClick={newEvent}>new event</button>
        <button onClick={newUpdate}>new update</button>
        <button onClick={newAssignment}>new assignment</button>
        <ToastContainer />
      </div>

      <div className="App">
        <Routes>
          {/* Redirect to login page if no specific route is provided */}
          <Route path="/" element={<Navigate to="/login" />} />

          {/* Other routes */}
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
