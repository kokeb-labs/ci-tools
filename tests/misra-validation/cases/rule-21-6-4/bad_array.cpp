// Seeded violation: the unsized global operator delete[] is replaced, the sized operator delete[] is not.
#include <cstdlib>
#include <new>

void operator delete[](void* block) noexcept { std::free(block); }  // seeded
