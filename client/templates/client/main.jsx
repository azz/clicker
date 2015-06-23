'use strict';

class BubbleSort extends React.Component {

    constructor(props) {
        super (props);
        this.state = {
          indices: [0, 1]
        };
    }

    componentDidMount() {
        this.setState({ indices: [
            this.props.lower_index, this.props.lower_index + 1
        ] });
    }

    swap(e) {
        $.post(this.props.swapURL, {
            lower_index: this.state.indices[0],
            bubble_sort: 'http://' + window.location.host + this.props.url
        })
        .then(res => console.log)
        .fail(res => console.error);
    }

    render() {
        return (
            <div>
                <p>
                Press the swap button to swap at interval <strong>{this.state.indices[0]}</strong>:
                </p>
                <a onClick={this.swap.bind(this)}
                   className="waves-effect waves-light btn-large">
                    <i className="mdi-action-swap-horiz left"></i>
                    Swap!
                </a>
            </div>
        );
    }
}

let run = function () {
    $.ajaxSetup({
        beforeSend: req => {
            req.setRequestHeader('X-CSRFToken', $.cookie('csrftoken'));
        }
    });

    var instance = parseInt($.url().param('instance')) || 1,
        lower_index = parseInt($.url().param('lower_index')) || 0,
        url = "/api/bubblesort/view/#/".replace('#', String(instance));

    React.render(
        <BubbleSort url={url} swapURL="/api/bubblesort/swap/" lower_index={lower_index} date={new Date()}/>,
        document.getElementById('react-main')
    );
};
run();