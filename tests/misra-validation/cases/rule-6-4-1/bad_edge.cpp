// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_4_1::bad_edge {

class Gauge {
 public:
  std::int32_t read() const {
    std::int32_t level = 0;  // hides the member level
    return level;
  }

 private:
  std::int32_t level{3};
};

std::int32_t clip(std::int32_t limit) {
  std::int32_t out = 0;
  if (limit > 0) {
    std::int32_t limit = 1;  // hides the parameter
    out = limit;
  }
  return out;
}

std::int32_t via_lambda(std::int32_t v) {
  const auto f = [](std::int32_t v) { return v; };  // the lambda parameter hides v
  return f(v);
}

}  // namespace kv::rule_6_4_1::bad_edge
