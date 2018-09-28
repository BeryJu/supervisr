import * as moment from 'moment';

export class Model {

    private unravel(): void {
        // unravel builtin type-hints from API
        // like converting timestamp into Date() objects
        let singleUnravel = (key, value, type) => {
            switch (type) {
                case 'timedelta':
                    return moment().subtract(value, 'seconds').fromNow();
                default:
                    return value;
            }
        };
        let walker = root => {
            for (const key in root) {
                if (root.hasOwnProperty(key)) {
                    let element = root[key];
                    let typeKey = key + '__type';
                    // Unravel single key
                    if (typeKey in root) {
                        let type = root[typeKey];
                        root[key] = singleUnravel(key, element, type);
                    }
                    // Further walk objects
                    if (typeof element === 'object') {
                        walker(element);
                    }
                }
            }
        };
        walker(this);
    }

    fromObject(source: Object): Model {
        Object.assign(this, source);
        this.unravel();
        return this;
    }

}
