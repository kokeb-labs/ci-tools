// Seeded violation: offsetof in a function template and in a constant.
#include <cstddef>
#include <cstdint>

namespace kv::rule_21_2_4::bad_template {

struct Header {
  std::uint8_t kind;
  std::uint16_t length;
};

template <typename T>
std::size_t second_field() {
  return offsetof(T, length);  // seeded
}

constexpr std::size_t kLengthAt = offsetof(Header, length);  // seeded

std::size_t both() { return second_field<Header>() + kLengthAt; }

}  // namespace kv::rule_21_2_4::bad_template
