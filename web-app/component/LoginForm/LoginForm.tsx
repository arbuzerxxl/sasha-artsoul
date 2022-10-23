import React, { useCallback, useEffect } from "react";
import Grid2 from '@mui/material/Unstable_Grid2';
import { Button, Typography } from '@mui/material';
import { Input } from '@mui/material';
import { useStore } from "effector-react";
import Cookies from 'js-cookie';

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

  const x = useCallback(async (data) => {
    const csrftoken = Cookies.get('csrftoken');
console.log(data);
    if (csrftoken) {
      const response = await fetch('/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          // 'Cookie': `csrftoken=${csrftoken}`,
          // "Set-Cookie": 'csrftoken=${csrftoken}',
          // 'X-CSRFToken': csrftoken,
          // 'X-XSRF-TOKEN': csrftoken
        },
        body: JSON.stringify({
          password: '1234',
          userName: '89171919745'
        }),
      });
      console.log(response);
    }

  }, []);

  // useEffect(() => {
  //   x()
  // }, []);

  return (
    <Grid2 className={styles.container} spacing={1}>
      <Typography
        align='center'
      >
        Логин
      </Typography>
      <form onSubmit={x} className={styles.form}>
        <Input
          value={loginStore}
          name='login'
          className={styles.input}
          placeholder='номер телефона'
          onChange={(e) => onChangeLoginStore(e.target.value)}
        />
        <Input
          value={passwordStore}
          name='password'
          className={styles.input}
          placeholder='пароль'
          onChange={(e) => onChangePasswordStore(e.target.value)}
        />
        <Button type="submit">Войти</Button>
      </form>
    </Grid2>
  )
}

export default React.memo(LoginForm);
