import Box from "@mui/material/Box";

export default function RichText({ value }: { value: string }) {
  return (
    <Box>
      <Box
        dangerouslySetInnerHTML={{ __html: value }}
        textAlign="justify"
        sx={{
          "& .responsive-object": {
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
        }}
      />
      {/* Clearfix */}
      <Box sx={{ clear: "both" }} />
    </Box>
  );
}
