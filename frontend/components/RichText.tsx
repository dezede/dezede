import Box from "@mui/material/Box";

export default function RichText({ value }: { value: string }) {
  return (
    <Box>
      <Box
        dangerouslySetInnerHTML={{ __html: value }}
        textAlign="justify"
        sx={{
          ".responsive-object": {
            position: "relative",
            clear: "both",
            "& iframe, & object, & embed": {
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
            },
          },
          "align-center, align-right": {
            display: "block",
          },
          "align-center": {
            textAlign: "center",
          },
          "align-right": {
            textAlign: "right",
          },
          hr: {
            border: "1px solid rgba(0, 0, 0, 0.12)",
            borderTop: "none",
            maxWidth: "10rem",
            marginLeft: 0,
          },
        }}
      />
      {/* Clearfix */}
      <Box sx={{ clear: "both" }} />
    </Box>
  );
}
