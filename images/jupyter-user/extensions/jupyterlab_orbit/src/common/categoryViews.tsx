import React from 'react';
import { ToolbarButtonComponent } from '@jupyterlab/apputils';
import { refreshIcon, closeIcon } from '@jupyterlab/ui-components';
import ReactJson from 'react-json-view';

const SECTION_CLASS = 'jp-RunningSessions-section';
const SECTION_HEADER_CLASS = 'jp-RunningSessions-sectionHeader';
const CONTAINER_CLASS = 'jp-RunningSessions-sectionContainer';
const LIST_CLASS = 'jp-RunningSessions-sectionList';

export const CategoryViews = (props: {
  name: string;
  items: JSX.Element;
  refreshCallback: (name: string) => any;
  closeAllCallback: (name: string) => void;
}) => {
  return (
    <div className={SECTION_CLASS}>
      <header className={SECTION_HEADER_CLASS}>
        <h2>{props.name}</h2>
        <div style={{ display: 'flex', alignItems: 'right' }}>
          <ToolbarButtonComponent
            tooltip={'Refresh List'}
            icon={refreshIcon}
            onClick={() => props.refreshCallback(props.name)}
          />
          <ToolbarButtonComponent
            tooltip={'Close All'}
            icon={closeIcon}
            onClick={() => props.closeAllCallback(props.name)}
          />
        </div>
      </header>
      <div className={CONTAINER_CLASS}>
        <ul className={LIST_CLASS}> {props.items} </ul>
      </div>
    </div>
  );
};

export const ListViewWithoutToolbar = (props: {
  name: string;
  items: JSX.Element;
}) => {
  return (
    <div className={SECTION_CLASS}>
      <header className={SECTION_HEADER_CLASS}>
        <h2>{props.name}</h2>
        <div style={{ display: 'flex', alignItems: 'right' }} />
      </header>
      <div className={CONTAINER_CLASS}>
        <ul className={LIST_CLASS}> {props.items} </ul>
      </div>
    </div>
  );
};

export const TreeView = (props: {
  name: string;
  item: any;
  root_name: string;
}) => {
  return (
    <div className={SECTION_CLASS}>
      <header className={SECTION_HEADER_CLASS}>
        <h2>{props.name}</h2>
        <div style={{ display: 'flex', alignItems: 'right' }} />
      </header>
      <div className={CONTAINER_CLASS}>
        <ReactJson
          src={props.item}
          name={props.root_name}
          collapsed={1}
          displayDataTypes={false}
        />
      </div>
    </div>
  );
};