// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_9_OK_NEAR_HPP
#define KV_RULE_8_2_9_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_2_9::ok_near {

enum class Kind : std::uint8_t { kCircle, kSquare };

class Shape {
 public:
  Shape() = default;
  Shape(Shape const&) = default;
  Shape(Shape&&) noexcept = default;
  Shape& operator=(Shape const&) = default;
  Shape& operator=(Shape&&) noexcept = default;
  virtual ~Shape() = default;
  [[nodiscard]] virtual Kind kind() const { return Kind::kCircle; }
};

inline bool same_kind(Shape const& a, Shape const& b) { return a.kind() == b.kind(); }

}  // namespace kv::rule_8_2_9::ok_near

#endif  // KV_RULE_8_2_9_OK_NEAR_HPP
