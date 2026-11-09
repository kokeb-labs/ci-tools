// Seeded violation: std::move of a member inside a const member function, and of a const T& in a template.
#include <array>
#include <cstdint>
#include <utility>

namespace kv::rule_28_6_1::bad_member {

struct Buffer {
  std::array<std::uint8_t, 4U> data;
};

class Holder {
 public:
  [[nodiscard]] Buffer take() const { return std::move(buffer_); }  // seeded

 private:
  Buffer buffer_{};
};

template <typename T>
T duplicate(const T& value) {
  return std::move(value);  // seeded
}

Buffer both(const Holder& h, const Buffer& b) {
  static_cast<void>(duplicate(b));
  return h.take();
}

}  // namespace kv::rule_28_6_1::bad_member
