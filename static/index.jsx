////////////////////////////////////////////////////////////////////////
//BookList
//callback function

function redirectSearch() {
    window.location.href="/search"
};

function postBookSelect(book_id) {
    // $.post("/bookselect", book_id, redirectSearch)
    
    fetch("/bookselect", {
            method: "POST",
            headers: {"Content-type" : "application/x-www-form-urlencoded; charset=UTF-8"},
            body : "book_id="+book_id
        })
        .then(() => redirectSearch());
};


const BookListItem = ({book, onBookSelect}) => {
    const imageURL = book.best_book.small_image_url;
    const bookName = book.best_book.title
    const book_id = book.best_book.id["#text"]

//Use a callback function to make an AJAX/Fetch Post, then redirect separately (window.location.href=url)

    return (
        <li onClick={() => postBookSelect(book_id)}> 
            <div>
            <img src={imageURL} />
            <p id="bookTitle">{bookName}</p>

            </div> 
        </li>
    );


};

const BookList =  (props) => {
    const bookItems = props.books.map((book) => {

        return(
            <BookListItem
                onBookSelect={props.onBookSelect}
                key={book.best_book.id["#text"]}
                book={book} />
            );
    });

    return (
        <ul>
        {bookItems}
        </ul>
    );
};



/////////////////////////////////////////////////////////////////////////
//SearchBar
class SearchBar extends React.Component {
    constructor (props) {
        super(props);

        this.state = { term: ''};
    }

    render () {
        return (
            <div className="search-bar">
                <input
                    value={this.state.term}
                    onChange={event => this.onInputChange(event.target.value)} />
                    </div>
        );
    }

    onInputChange(term) {
        this.setState({term})
        this.props.onSearchTermChange(term);
    }
}

////////////////////////////////////////////////////////////////////////
//Index
class App extends React.Component {
    constructor (props){
        super(props);

        this.state = {
            books: [],
            selectedBook: null
        };

        this._debouncedBookSearch = _.debounce( (term) => this._bookSearch(term), 500);
    }

    _bookSearch(term) {
        // const book_data = { "booksearch" : term }
        

        fetch("/interim-search", {
            method: "POST",
            headers: {"Content-type" : "application/x-www-form-urlencoded; charset=UTF-8"},
            body : "booksearch="+term
        })
            .then(function(response) {
                return response.json();
            })
            // .then(function(myJson) {
            //     console.log(JSON.stringify(myJson));
            // });
            .then((myJson) => {
                console.log(myJson)
                this.setState({
                    books : myJson
                })
            });
        

    }

    render () {
        
        console.log(this.state)

        return (

                <div>
                    <SearchBar onSearchTermChange={this._debouncedBookSearch}/>
                    <BookList
                        onBookSelect={selectedBook => this.setState({selectedBook})}
                        books={this.state.books} />
                </div>
        
        );
    }
}



ReactDOM.render(<App />, document.getElementById('root'));
