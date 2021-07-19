// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        posts: [], // See initialization.
        post_content: "", // for th post being edited or added
        show_post: false, //showing the new post text box
        show_reply: null, // replying to a post
        author_name: author_name,
        user_email: user_email,
    };

    app.index = (a) => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of a) {
            p._idx = i++;
            // TODO: Only make the user's own posts editable.
            p.editable = true;
            p.edit = false;
            p.is_pending = false;
            p.error = false;
            p.original_content = p.content; // Content before an edit.
            p.server_content = p.content; // Content on the server.
        }
        return a;
    };

    app.reindex = () => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of app.vue.posts) {
            p._idx = i++;
        }
    };

    app.clear_post = () => {
        app.vue.post_content = "";
    };

    app.toggle_post = (toggle = !app.vue.show_post) => {
        app.clear_post()
        app.vue.show_reply = null
        app.vue.show_post = toggle
    };

    app.toggle_reply = (_idx) => {
      app.clear_post()
        //make sure editing only one ata time
        // app.vue.posts.forEach((post) => (post.edit = false))
        app.vue.show_post = false;
        app.vue.show_reply = _idx
    };

    // set editing to true for the post, but no other post can be dited
    app.do_edit = (post_idx) => {
        // Handler for button that starts the edit.
        // TODO: make sure that no OTHER post is being edited.
        app.vue.posts.forEach((post) => (post.edit = false))
        app.vue.show_post = false
        app.vue.show_reply = null
        // If so, do nothing.  Otherwise, proceed as below.
        let p = app.vue.posts[post_idx];
        p.edit = true;
        p.is_pending = false;
    };

    // canceling an edit, turn off edit and clear anything in there
    app.do_cancel = (post_idx) => {
        // Handler for button that cancels the edit.
        app.clear_post()
        let p = app.vue.posts[post_idx];
        /*
        if (p.id === null) {
            // If the post has not been saved yet, we delete it.
            app.vue.posts.splice(post_idx, 1);
            app.reindex();
        } else {
            // We go back to before the edit.
            p.edit = false;
            p.is_pending = false;
            p.content = p.original_content;
        }

         */
        p.edit = false;
        p.content = p.original_content;

    }

    // if theres something to save, then save it to post
    app.do_save = (post_idx) => {
        // Handler for "Save edit" button.
        let p = app.vue.posts[post_idx];
        if (p.content !== p.server_content) {
            p.is_pending = true;
            axios.post(posts_url, {
                content: p.content,
                id: p.id,
                is_reply: p.is_reply,
            }).then((result) => {
                console.log("Received:", result.data);
                // TODO: You are receiving the post id (in case it was inserted),
                // and the content.  You need to set both, and to say that
                // the editing has terminated.
                p.original_content = p.content
                p.server_content = p.content
                p.edit = false

            }).catch(() => {
                p.is_pending = false;
                console.log("Caught error");
                // We stay in edit mode.
            });
        } else {
            // No need to save.
            p.edit = false;
            p.original_content = p.content;
        }
    }

    app.get_posts = () => {
        axios.get(posts_url).then((result) => {
            app.vue.posts = app.index(result.data.posts)
        })
    };

    app.add_post = () => {
        // TODO: this is the new post we are inserting.
        // You need to initialize it properly, completing below, and ...
        // takes care of sending empty posts
        if(app.vue.post_content.length == 0){
            return
        }

        let q = {
            id: null,
            edit: null,
            editable: null,
            content: "",
            server_content: null,
            original_content: "",
            author: null,
            email: null,
            is_reply: null,
        };
        // TODO:
        // ... you need to insert it at the top of the post list.

        axios.post((posts_url), {
            id: null,
            is_reply: null,
            content: app.vue.post_content
        }).then((result) => {
            // need to update the value of the q dictionary from above
            q = {
                ...q,
                id: result.data.id,
                editable: true,
                content: app.vue.post_content,
                original_content: app.vue.post_content,
                server_content: app.vue.post_content,
                author: author_name,
                email: user_email
            }
            //create array with q in the front and the rst following it
            app.vue.posts = [q, ...app.vue.posts]
            app.reindex();
            app.toggle_post(false)



        })
    };

    app.reply = (post_idx) => {
        let p = app.vue.posts[post_idx];
        if (p.id !== null) {
            // TODO: this is the new reply.  You need to initialize it properly...
            let q = {
                id: null,
                edit: null,
                editable: null,
                content: "",
                server_content: null,
                original_content: "",
                author: null,
                email: null,
                is_reply: null,
            };
            // TODO: and you need to insert it in the right place, and reindex
            // the posts.  Look at the code for app.add_post; it is similar.
            axios.post(posts_url, {
                id:null,
                is_reply: p.id,
                content: app.vue.post_content
            }).then((result) => {
                // post the reply in reverse chronological order BUT under thr main post
                q = {
                    ...q,
                    id: result.data.id,
                    editable: true,
                    content: result.data.content,
                    original_content: result.data.content,
                    server_content: result.data.content,
                    author: author_name,
                    email: user_email,
                    is_reply: p.id
                };
                // add this 1 post after the main post with the data above q
                // 0 mean remove mothing
                app.vue.posts.splice(post_idx + 1, 0, q)
                app.reindex()
                //hide the reply box
                app.toggle_reply(null)
            }).catch(e => {
                console.log(e);
            })
        }
    };

    app.do_delete = (post_idx) => {
        let p = app.vue.posts[post_idx];
        //delete post from server
        axios.post(delete_url, {
            id: p.id,
        }).then(() => {
            app.vue.posts.splice(post_idx, 1);
        })
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        do_edit: app.do_edit,
        do_cancel: app.do_cancel,
        do_save: app.do_save,
        add_post: app.add_post,
        reply: app.reply,
        do_delete: app.do_delete,
        toggle_post: app.toggle_post,
        toggle_reply: app.toggle_reply,


    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // You should load the posts from the server.
        // This is purely debugging code.
        /*
        posts = [
            // This is a post.
            {
                id: 1,
                content: "I love apples",
                author: "Joe Smith",
                email: "joe@ucsc.edu",
                is_reply: null, // Main post.  Followed by its replies if any.
            },
            {
                id: 2,
                content: "I prefer bananas",
                author: "Elena Degiorgi",
                email: "elena@ucsc.edu",
                is_reply: 1, // This is a reply.
            },
            {
                id: 3,
                content: "I prefer bananas",
                author: "Elena Degiorgi",
                email: "elena@ucsc.edu",
                is_reply: 1, // This is a reply.
            },
        ];
         */

        // TODO: Load the posts from the server instead.
        // We set the posts.
        // app.vue.posts = app.index(posts);
        app.get_posts()
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
