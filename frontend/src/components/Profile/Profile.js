import React from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { useNavigate } from "react-router-dom";
import * as Yup from "yup";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import styles from "./Profile.module.css";
import { toast } from "react-toastify";

const ProfileSchema = Yup.object().shape({
  fullName: Yup.string().max(50, "Max 50 characters").required("Required"),
  address1: Yup.string().max(100, "Max 100 characters").required("Required"),
  address2: Yup.string().max(100, "Max 100 characters"),
  city: Yup.string().max(100, "Max 100 characters").required("Required"),
  state: Yup.string().required("Required"),
  zip: Yup.string()
    .matches(/^\d{5}(-\d{4})?$/, "Must be a valid zip code (e.g. 12345 or 12345-6789)")
    .required("Required"),
  skills: Yup.array().min(1, "Select at least one skill").required("Required"),
  availability: Yup.array()
    .min(1, "Select at least one date")
    .required("Required"),
  preferences: Yup.string().max(500, "Max 500 characters"),
});

const US_STATES = [
  "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
  "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
  "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
  "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
  "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
];

const SKILL_OPTIONS = [
  "organizing", "communication", "tech", "leadership", "marketing",
  "public speaking", "fundraising", "writing", "social media",
  "graphic design", "event planning",
];

const initialValues = {
  fullName: "",
  address1: "",
  address2: "",
  city: "",
  state: "",
  zip: "",
  skills: [],
  availability: [],
  preferences: "",
};

const Profile = () => {
  const navigate = useNavigate();

  const handleProfileSubmit = (values, { setSubmitting }) => {
    console.log("Profile Updated!", values);
    toast.success("Profile Updated Successfully!");
    setSubmitting(false);
    navigate("/volunteerMatch");
  };

  return (
    <div className={styles.profileContainer}>
      <h2>Manage Profile</h2>
      <Formik
        initialValues={initialValues}
        validationSchema={ProfileSchema}
        onSubmit={handleProfileSubmit}
      >
        {({ isSubmitting, setFieldValue, values }) => (
          <Form>
            <div>
              <label htmlFor="fullName">Full Name</label>
              <Field type="text" name="fullName" />
              <ErrorMessage name="fullName" component="div" className={styles.error} />
            </div>

            <div>
              <label htmlFor="address1">Address 1</label>
              <Field type="text" name="address1" />
              <ErrorMessage name="address1" component="div" className={styles.error} />
            </div>

            <div>
              <label htmlFor="address2">Address 2</label>
              <Field type="text" name="address2" />
              <ErrorMessage name="address2" component="div" className={styles.error} />
            </div>

            <div>
              <label htmlFor="city">City</label>
              <Field type="text" name="city" />
              <ErrorMessage name="city" component="div" className={styles.error} />
            </div>

            <div>
              <label htmlFor="state">State</label>
              <Field as="select" name="state">
                <option value="">Select</option>
                {US_STATES.map((st) => (
                  <option key={st} value={st}>{st}</option>
                ))}
              </Field>
              <ErrorMessage name="state" component="div" className={styles.error} />
            </div>

            <div>
              <label htmlFor="zip">Zip Code</label>
              <Field type="text" name="zip" />
              <ErrorMessage name="zip" component="div" className={styles.error} />
            </div>

            <div>
              <label htmlFor="skills">Skills</label>
              <Field as="select" name="skills" multiple>
                {SKILL_OPTIONS.map((skill) => (
                  <option key={skill} value={skill}>
                    {skill.charAt(0).toUpperCase() + skill.slice(1)}
                  </option>
                ))}
              </Field>
              <ErrorMessage name="skills" component="div" className={styles.error} />
            </div>

            <div>
              <label htmlFor="availability">Availability</label>
              <DatePicker
                selected={values.availability.length > 0 ? values.availability[0] : null}
                onChange={(date) => {
                  if (date instanceof Date && !isNaN(date)) {
                    const updated = values.availability.some(
                      (d) => d.toDateString() === date.toDateString()
                    )
                      ? values.availability.filter(
                          (d) => d.toDateString() !== date.toDateString()
                        )
                      : [...values.availability, date];
                    setFieldValue("availability", updated);
                  }
                }}
                placeholderText="Select dates"
                className={styles.datePicker}
                shouldCloseOnSelect={false}
                isClearable
                inline
              />
              <ErrorMessage name="availability" component="div" className={styles.error} />
            </div>

            <div>
              <label htmlFor="preferences">Preferences</label>
              <Field as="textarea" name="preferences" />
              <ErrorMessage name="preferences" component="div" className={styles.error} />
            </div>

            <button className={styles.submit} type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Updating..." : "Update Profile"}
            </button>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default Profile;
