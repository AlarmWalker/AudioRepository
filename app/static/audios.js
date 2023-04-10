var app = new Vue({
    el: "#app",
  
    //------- data --------
    data: {
      serviceURL: "https://cs3103.cs.unb.ca:8024",
      authenticated: false,
      loggedIn: null,
      libraryData: null,
      audioData: null,
      userData: null,
      modalAdd: false,
      input: {
        username: "",
        password: ""
      },
      audioForm: {
        audioName: "",
        audioFile: null
      }
    },
    methods: {
      login() {
        if (this.input.username != "" && this.input.password != "") {
          axios
          .post(this.serviceURL+"/signin", {
              "username": this.input.username,
              "password": this.input.password
          })
          .then(response => {
              if (response.data.status == "success") {
                this.authenticated = true;
                this.loggedIn = response.data.user_id;
                this.getCurrentUser();
                console.log(this.loggedIn);
              }
          })
          .catch(e => {
              alert("The username or password was incorrect, try again");
              this.input.password = "";
              console.log(e);
          });
        } else {
          alert("A username and password must be present sss");
        }
      },
  
  
      logout() {
        axios
        .delete(this.serviceURL+"/signin")
        .then(response => {
            if (response.data.status == "success") {
                this.authenticated = false;
                this.loggedIn = NULL
              }
            location.reload();
        })
        .catch(e => {
            alert("user is not logged in");
            console.log(e);
        });


        
      },
      getCurrentUser(){
        axios
        .get(this.serviceURL+"/users/" + this.loggedIn)
        .then(response => {
          this.userData = response.data.user;
        })
        .catch(e => {
          alert("Unable to load the requested user");
          console.log(e);
        });
      },
      fetchUserAudioLib() {
        axios
        .get(this.serviceURL+"/users/" + this.loggedIn + "/audios")
        .then(response => {
            this.libraryData = response.data.library;
        })
        .catch(e => {
          alert("Unable to load the audio library");
          console.log(e);
        });
      },
      addAudio(){
        let fileInput = document.getElementById('audioFile');
        let selectedFile = fileInput.files[0];
        let fileName = selectedFile.name;
        const audioFile = document.getElementById('audioFile').files[0];
        const audioName = document.getElementById('audioName').value;
        const formData = new FormData();
        formData.append('file', audioFile);
        formData.append('audioName', audioName);
        if (this.audioForm.audioName !== "" && this.audioForm.audioFile.size !== null) {
          axios
          .post(this.serviceURL + "/users/" + this.loggedIn + "/audios", {
            "audioName": this.audioForm.audioName,
            "audioFile": "audios/" + fileName
          })
          .catch(e => {
            alert("unable to add the audio file");
            console.log(e);
          })
          axios.post('/FileUpload', formData)
          .then(response => {
            if (response.data.status === 'success') {
              this.modalAdd=false;
              alert('Audio added successfully');
            }
          })
          .catch(error => {
            console.error(error);
            alert('Unable to add audio');
          });
        }
      },
      showModalAdd() {
        this.modalAdd = true;
      },
      hideModal(){
        this.modalAdd = false;
      }
  
  
    }
    //------- END methods --------
  
  });
