// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_11_TRIVIAL_OK_NEAR_HPP
#define KV_RULE_8_2_11_TRIVIAL_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_2_11_trivial::ok_near {

enum class Mode : std::int32_t { kOff, kOn };

std::int32_t take(std::int32_t count, ...);

inline std::int32_t use(std::int32_t const* p) { return take(std::int32_t{2}, p, Mode::kOn); }

// A user-provided copy assignment is not one of the inappropriate properties: the copy constructor and the
// destructor stay trivial, so the object may go through the ellipsis.
struct Handle {
  Handle() = default;
  Handle(Handle const&) = default;
  Handle& operator=(Handle const& other) {
    value = other.value;
    return *this;
  }
  std::int32_t value{0};
};

inline std::int32_t use_handle() {
  Handle const h{};
  return take(std::int32_t{1}, h);
}

}  // namespace kv::rule_8_2_11_trivial::ok_near

#endif  // KV_RULE_8_2_11_TRIVIAL_OK_NEAR_HPP
