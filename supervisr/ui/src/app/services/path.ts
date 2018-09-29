import { Actions } from './actions';

export class APIPath {

    app = '';
    component = '';
    action: Actions | string = '';

    static fromString(source: string): APIPath {
        const parts = source.split('::');
        const path = new APIPath();
        path.app = parts[0];
        path.component = parts[1];
        path.action = parts[2];
        return path;
    }

}
