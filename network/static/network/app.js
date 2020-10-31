const textInput = document.querySelector("#text-form");
const follow = document.querySelector("#follow");
const posts = document.querySelector("#posts");

posts &&
  posts.addEventListener("click", (event) => {
    if (event.target.tagName == "A" && event.target.href.slice(-1) == "#") {
      event.preventDefault();
      fetch("/like", {
        method: "POST",
        body: JSON.stringify({
          post: event.target.id.substring(1),
        }),
      })
        .then((response) => response.json())
        .then((post) => {
          const el = document.querySelector(`#${event.target.id}`);
          const likes = document.querySelector(`#${event.target.id}p`);
          if (post.icon === "yes") {
            el.innerHTML = `<i class="far fa-heart"></i>`;
          } else {
            el.innerHTML = `<i class="fas fa-heart"></i>`;
          }
          likes.innerHTML = `<i class="fab fa-gratipay"></i> ${post.likes}`;
        });
    } else if (
      (event.target.tagName = "B" && event.target.id.startsWith("b"))
    ) {
      event.preventDefault();
      const el = document.querySelector(`#d${event.target.id.slice(1)}`);
      const content = el.querySelector("p").innerText;
      el.innerHTML = `<form method="POST" action="/edit" id="edit">
    <textarea cols="30" rows="4" id="text">${content}</textarea>
    <div>
        <input type="submit" class="btn btn-info" value="Edit" id="km">
    </div>
    </form>`;
      const edit = document.querySelector("#edit");
      edit &&
        edit.addEventListener("submit", (event) => {
          event.preventDefault();
          const content = edit.querySelector("#text").value;
          if (content.length == 0) return;

          fetch("/edit", {
            method: "POST",
            body: JSON.stringify({
              content: content,
              id: edit.parentElement.id.toString(),
            }),
          })
            .then((response) => response.json())
            .then((post) => {
              newPost = edit.parentElement;
              newPost.innerHTML = `<div class="card-body">
              <div class="card-headers">
                <h5 class="card-title"><a href="/profile/${post.user_id}">${post.username}</a></h5>
                <button class="btn btn-warning edit-btn" id="b${post.id}">Edit</button>
              </div>
              <p class="card-text">${post.content}</p>
              <p class="card-text">${post.time_posted}</p>
              <p class="card-text" id="p${post.id}p"><i class="fab fa-gratipay"></i> ${post.likes}</p>
            </div>`;
            });
        });
    }
  });

textInput &&
  textInput.addEventListener("submit", (event) => {
    event.preventDefault();
    const content = document.querySelector("#text").value;
    if (content.length == 0) return;

    fetch("/new_post", {
      method: "POST",
      body: JSON.stringify({
        content: content,
      }),
    })
      .then((response) => response.json())
      .then((post) => {
        const div = document.querySelector("#posts");
        const newPost = document.createElement("div");
        newPost.className = "card";
        newPost.style.width = "22rem";
        newPost.style.marginLeft = "auto";
        newPost.style.marginRight = "auto";
        newPost.id = `d${post.id}`;
        newPost.innerHTML = `<div class="card-body">
            <div class="card-headers">
              <h5 class="card-title"><a href="{% url 'profile' ${post.user_id} %}">${post.username}</a></h5>
              <button class="btn btn-warning edit-btn" id="b${post.id}">Edit</button>
            </div>
            <p class="card-text">${post.content}</p>
            <p class="card-text">${post.time_posted}</p>
            <p class="card-text" id="p${post.id}p"><i class="fab fa-gratipay"></i> ${post.likes}</p>
          </div>`;
        div.insertBefore(newPost, div.firstChild);
        document.querySelector("#text").value = "";
      });
  });

follow &&
  follow.addEventListener("click", (event) => {
    event.preventDefault();
    let user = window.location.pathname.split("/").slice(-1)[0];
    fetch("/follow", {
      method: "POST",
      body: JSON.stringify({
        user: user,
      }),
    })
      .then((response) => response.json())
      .then((post) => {
        const el = document.querySelector("#followers");
        el.innerText = `Followers: ${post.followers}`;
        if (post.icon == "yes") {
          follow.innerText = "Follow";
          follow.classList.remove("btn-danger");
          follow.classList.add("btn-success");
        } else {
          follow.innerText = "Unfollow";
          follow.classList.remove("btn-success");
          follow.classList.add("btn-danger");
        }
      });
  });
