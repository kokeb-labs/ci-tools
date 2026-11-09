// The translation unit that compiles the fixture's header.
#include "fixture.hpp"

namespace fixture {

std::uint32_t use_all(std::uint32_t v) { return sum(v) ^ twice(v) ^ mask(v) ^ low(v); }

}  // namespace fixture
