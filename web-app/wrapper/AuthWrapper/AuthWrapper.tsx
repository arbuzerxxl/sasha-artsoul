import React from 'react';

type Props = {
  children: React.ReactNode;
}

const AuthWrapper = (props: Props) => {
  const { children } = props;
  return (
    <>
      {children}
    </>
  )
};

export default AuthWrapper;
