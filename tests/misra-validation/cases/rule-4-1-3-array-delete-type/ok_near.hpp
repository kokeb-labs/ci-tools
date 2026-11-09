// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_3_ARRAY_DELETE_TYPE_OK_NEAR_HPP
#define KV_RULE_4_1_3_ARRAY_DELETE_TYPE_OK_NEAR_HPP

#include <array>
#include <cstdint>

namespace kv::rule_4_1_3_array_delete_type::near {

// Polymorphic objects in a fixed array of the derived type, used through a base reference: no deletion.
struct Shape {
  Shape() = default;
  Shape(const Shape&) = delete;
  Shape(Shape&&) = delete;
  Shape& operator=(const Shape&) = delete;
  Shape& operator=(Shape&&) = delete;
  virtual ~Shape() = default;
  [[nodiscard]] virtual std::uint32_t sides() const { return 0U; }
};
struct Square final : Shape {
  Square() = default;
  Square(const Square&) = delete;
  Square(Square&&) = delete;
  Square& operator=(const Square&) = delete;
  Square& operator=(Square&&) = delete;
  ~Square() override = default;
  [[nodiscard]] std::uint32_t sides() const override { return 4U; }
};
inline std::uint32_t total(const std::array<Square, 2>& squares) {
  const Shape& first = squares[0];
  return first.sides();
}

}  // namespace kv::rule_4_1_3_array_delete_type::near

#endif  // KV_RULE_4_1_3_ARRAY_DELETE_TYPE_OK_NEAR_HPP
