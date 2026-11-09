// Edge cases of the seeded violation.
#include <cstdint>
#include <cstring>

namespace kv::rule_8_18_1::bad_edge {

void slide(std::uint8_t (&data)[8]) { std::memcpy(&data[0], &data[1], 6U); }

union Raw {
  std::uint32_t u;
  float f;
};

std::uint32_t pun() {
  Raw r{};
  r.f = 1.0F;
  r.u = static_cast<std::uint32_t>(r.f);
  return r.u;
}

}  // namespace kv::rule_8_18_1::bad_edge
