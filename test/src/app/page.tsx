import React from "react";
import { Vortex } from "../ui/vortex";

export default function VortexDemo() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-8">
      <div
        className="w-[calc(100%-4rem)] mx-auto rounded-md h-[30rem] overflow-hidden">
        <Vortex
          backgroundColor="transparent"
          className="flex items-center flex-col justify-center px-2 md:px-10 py-4 w-full h-full">
          <div className="flex flex-col sm:flex-row items-center gap-4 mt-6">
            </div>
        </Vortex>
      </div>
    </div>
  );
}
