// Use this component only when the text was cleaned in the backend using whitelisting.

import Box from "@mui/material/Box";

export default function SafeText({ value }: { value: string }) {
  if (!value) {
    return null;
  }
  return (
    <Box
      component="span"
      dangerouslySetInnerHTML={{ __html: value }}
      sx={{
        sup: {
          // Trick so that exponents like `M<sup>lle</sup>` do not mess up the vertical alignment.
          lineHeight: 0,
        },
      }}
    />
  );
}
