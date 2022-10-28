import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const RemoveBg = () => {
  const [title, setTitle] = useState("");
  const [file, setFile] = useState("");
  const [preview, setPreview] = useState("");
  const navigate = useNavigate();
  const [apis, setApi] = useState("");

  const loadImage = (e) => {
    const image = e.target.files[0];
    setFile(image);
    setPreview(URL.createObjectURL(image));
  };

  const saveProduct = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("files[]", file);
    // formData.append("title", title);
    try {
      await axios
        .post("http://127.0.0.1:5000/v1/remove-bg", formData, {
          headers: {
            "Content-type": "multipart/form-data"
          }
        })
        .then(function (response) {
          console.log(response.data);
          setApi(response.data["ImageBytes"]);
        });
      // navigate("/");
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="container mt-5">
      <div className="columns is-centered mt-5">
        <div className="column is-half">
          <form onSubmit={saveProduct}>
            {/* <div className="field">
            <label className="label">Product Name</label>
            <div className="control">
              <input
                type="text"
                className="input"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Product Name"
              />
            </div>
          </div> */}

            <div className="field">
              <label className="label">Image</label>
              <div className="control">
                <div className="file">
                  <label className="file-label">
                    <input
                      type="file"
                      className="file-input"
                      onChange={loadImage}
                    />
                    <span className="file-cta">
                      <span className="file-label">Choose a file...</span>
                    </span>
                  </label>
                </div>
              </div>
            </div>

            {preview ? (
              <figure className="image is-128x128">
                <img src={preview} alt="Preview Image" />
              </figure>
            ) : (
              ""
            )}

            <div className="field">
              <div className="control">
                <button type="submit" className="button is-success">
                  Generate
                </button>
              </div>
            </div>
          </form>
          <div className="card">
            <div
              className="card-image mt-2"
              style={{ border: "5px solid rgba(255, 0, 144)" }}
            >
              <figure className="image is-4by3">
                <img src={`data:image/jpeg;base64,${apis}`} />
              </figure>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RemoveBg;
