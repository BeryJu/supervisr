import * as moment from 'moment';
import { createElement } from '@angular/core/src/view/element';

export class Model {

    private unravel(): void {
        // unravel builtin type-hints from API
        // like converting timestamp into Date() objects
        const singleUnravel = (key, value, type) => {
            switch (type) {
                case 'timedelta':
                    return moment().subtract(value, 'seconds').fromNow();
                case 'timestamp':
                    return moment.unix(value);
                case 'link':
                    const link = <HTMLAnchorElement>(document.createElement('a'));
                    link.href = value;
                    link.innerText = 'Link';
                    return link;
                default:
                    return value;
            }
        };
        const walker = root => {
            for (const key in root) {
                if (root.hasOwnProperty(key)) {
                    const element = root[key];
                    const typeKey = key + '__type';
                    // Unravel single key
                    if (typeKey in root) {
                        const type = root[typeKey];
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
