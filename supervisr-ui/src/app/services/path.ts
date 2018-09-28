import { Actions } from './actions';

export class APIPath {

    app: string = '';
    component: string = '';
    action: Actions | string = '';

    static fromString(source: string): APIPath {
        let parts = source.split('::');
        let path = new APIPath();
        path.app = parts[0];
        path.component = parts[1];
        path.action = parts[2];
        return path;
    }

}
