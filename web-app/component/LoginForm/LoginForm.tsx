import React, { useCallback, useEffect } from "react";
import Grid2 from '@mui/material/Unstable_Grid2';
import { Typography } from '@mui/material';
import { Input } from '@mui/material';
import { useStore } from "effector-react";

import {
  $loginStore,
  $passwordStore,
  onChangeLoginStore,
  onChangePasswordStore,
  resetLoginForm,
} from '../../store/loginForm';

import styles from './LoginForm.module.scss';

type Props = {

}

const LoginForm = (props: Props) => {
  const { } = props;

  const loginStore = useStore($loginStore);
  const passwordStore = useStore($passwordStore);

  useEffect(() => () => resetLoginForm(), []);

  const x = useCallback(async () => {
    const response = await fetch('', {
      method: 'PUT',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',

      },
      body: JSON.stringify({
        password: '',
        userName: ''
      }),
    });
    console.log(response);
  }, []);

  return (
    <Grid2 className={styles.container} spacing={1}>
      <Typography
        align='center'
      >
        Логин
      </Typography>
      <Input
        value={loginStore}
        className={styles.input}
        placeholder='номер телефона'
        onChange={(e) => onChangeLoginStore(e.target.value)}
      />
      <Input
        value={passwordStore}
        className={styles.input}
        placeholder='пароль'
        onChange={(e) => onChangePasswordStore(e.target.value)}
      />
    </Grid2>
  )
}

export default React.memo(LoginForm);
