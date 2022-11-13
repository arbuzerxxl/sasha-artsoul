
import { createEvent, createStore } from 'effector';

const $loginStore = createStore<string>('');
const $passwordStore = createStore<string>('');

const onChangeLoginStore = createEvent<string>();
const onChangePasswordStore = createEvent<string>();

const resetLoginForm = createEvent();

$loginStore.on(onChangeLoginStore, (_, v) => v);
$passwordStore.on(onChangePasswordStore, (_, v) => v);

$loginStore.reset(resetLoginForm);
$passwordStore.reset(resetLoginForm);

export {
  $loginStore,
  $passwordStore,
  onChangeLoginStore,
  onChangePasswordStore,
  resetLoginForm,
};
