import React from 'react';
import {useCheckout} from '@stripe/react-stripe-js';

const PayButton = () => {
  const { confirm } = useCheckout();
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const handleClick = () => {
    setLoading(true);
    confirm().then((result) => {
      if (result.type === 'error') {
        setError(result.error)
      }
      setLoading(false);
    })
  };

  return (
    <div className="mt-4 flex place-content-end">
      <button
          className="py-2 px-5 rounded-lg text-2xl text-amber-300 font-bold border-2 border-amber-300
                     hover:bg-amber-300 hover:text-black"
          onClick={handleClick}
          disabled={loading}
      >
        Pay
      </button>
      {error && <div>{error.message}</div>}
    </div>
  )
};

export default PayButton;
