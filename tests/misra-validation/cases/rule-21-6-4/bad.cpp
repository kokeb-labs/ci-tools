// Seeded violation: the unsized global operator delete is replaced, the sized one is not.
#include <cstdlib>
#include <new>

void operator delete(void* block) noexcept { std::free(block); }  // seeded
