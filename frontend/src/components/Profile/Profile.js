import React from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import styles from "./Profile.module.css";

// Validation schema for the profile form
const ProfileSchema = Yup.object().shape({
  fullName: Yup.string().max(50, "Max 50 characters").required("Required"),
  address1: Yup.string().max(100, "Max 100 characters").required("Required"),
  address2: Yup.string().max(100, "Max 100 characters"),
  city: Yup.string().max(100, "Max 100 characters").required("Required"),
  state: Yup.string().required("Required"),
  zip: Yup.string()
    .min(5, "Min 5 characters")
    .max(9, "Max 9 characters")
    .required("Required"),
  skills: Yup.array().min(1, "Select at least one skill").required("Required"),
  availability: Yup.string().required("Required"),
});

const Profile = () => {
  return (
    <div className={styles.profileContainer}>
      <h2>Manage Profile</h2>
      <Formik
        initialValues={{
          fullName: "",
          address1: "",
          address2: "",
          city: "",
          state: "",
          zip: "",
          skills: [],
          availability: "",
        }}
        validationSchema={ProfileSchema}
        onSubmit={(values) => {
          console.log("Profile Updated!", values);
          alert("Profile Updated Successfully!");
        }}
      >
        {({ isSubmitting }) => (
          <Form>
            <div>
              <label htmlFor="fullName">Full Name</label>
              <Field type="text" name="fullName" />
              <ErrorMessage
                name="fullName"
                component="div"
                className={styles.error}
              />
            </div>

            <div>
              <label htmlFor="address1">Address 1</label>
              <Field type="text" name="address1" />
              <ErrorMessage
                name="address1"
                component="div"
                className={styles.error}
              />
            </div>

            <div>
              <label htmlFor="address2">Address 2</label>
              <Field type="text" name="address2" />
              <ErrorMessage
                name="address2"
                component="div"
                className={styles.error}
              />
            </div>

            <div>
              <label htmlFor="city">City</label>
              <Field type="text" name="city" />
              <ErrorMessage
                name="city"
                component="div"
                className={styles.error}
              />
            </div>

            <div>
              <label htmlFor="state">State</label>
              <Field as="select" name="state">
                <option value="">Select</option>
                <option value="AL">Alabama</option>
                <option value="AK">Alaska</option>
                <option value="AZ">Arizona</option>
                <option value="AR">Arkansas</option>
                <option value="CA">California</option>
                <option value="CO">Colorado</option>
                <option value="CT">Connecticut</option>
                <option value="DE">Delaware</option>
                <option value="FL">Florida</option>
                <option value="GA">Georgia</option>
                <option value="HI">Hawaii</option>
                <option value="ID">Idaho</option>
                <option value="IL">Illinois</option>
                <option value="IN">Indiana</option>
                <option value="IA">Iowa</option>
                <option value="KS">Kansas</option>
                <option value="KY">Kentucky</option>
                <option value="LA">Louisiana</option>
                <option value="ME">Maine</option>
                <option value="MD">Maryland</option>
                <option value="MA">Massachusetts</option>
                <option value="MI">Michigan</option>
                <option value="MN">Minnesota</option>
                <option value="MS">Mississippi</option>
                <option value="MO">Missouri</option>
                <option value="MT">Montana</option>
                <option value="NE">Nebraska</option>
                <option value="NV">Nevada</option>
                <option value="NH">New Hampshire</option>
                <option value="NJ">New Jersey</option>
                <option value="NM">New Mexico</option>
                <option value="NY">New York</option>
                <option value="NC">North Carolina</option>
                <option value="ND">North Dakota</option>
                <option value="OH">Ohio</option>
                <option value="OK">Oklahoma</option>
                <option value="OR">Oregon</option>
                <option value="PA">Pennsylvania</option>
                <option value="RI">Rhode Island</option>
                <option value="SC">South Carolina</option>
                <option value="SD">South Dakota</option>
                <option value="TN">Tennessee</option>
                <option value="TX">Texas</option>
                <option value="UT">Utah</option>
                <option value="VT">Vermont</option>
                <option value="VA">Virginia</option>
                <option value="WA">Washington</option>
                <option value="WV">West Virginia</option>
                <option value="WI">Wisconsin</option>
                <option value="WY">Wyoming</option>
              </Field>
              <ErrorMessage
                name="state"
                component="div"
                className={styles.error}
              />
            </div>

            <div>
              <label htmlFor="zip">Zip Code</label>
              <Field type="text" name="zip" />
              <ErrorMessage
                name="zip"
                component="div"
                className={styles.error}
              />
            </div>

            <div>
              <label htmlFor="skills">Skills</label>
              <Field as="select" name="skills">
                <option value="">Select</option>
                <option value="organizing">Organizing</option>
                <option value="communication">Communication</option>
                <option value="tech">Tech</option>
                <option value="leadership">Leadership</option>
                <option value="marketing">Marketing</option>
                <option value="public speaking">Public Speaking</option>
                <option value="fundraising">Fundraising</option>
                <option value="writing">Writing</option>
                <option value="social media">Social Media</option>
                <option value="graphic design">Graphic Design</option>
                <option value="event planning">Event Planning</option>
                {/* Add more skills */}
              </Field>
              <ErrorMessage
                name="skills"
                component="div"
                className={styles.error}
              />
            </div>

            <div>
              <label htmlFor="availability">Availability</label>
              <Field type="text" name="availability" placeholder="MM/DD/YYYY" />
              <ErrorMessage
                name="availability"
                component="div"
                className={styles.error}
              />
            </div>

            <button type="submit" disabled={isSubmitting}>
              Update Profile
            </button>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default Profile;
