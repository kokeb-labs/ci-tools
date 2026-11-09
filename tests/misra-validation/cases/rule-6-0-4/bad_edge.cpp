// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_0_4::bad_edge {

struct App {
  std::int32_t main() const { return 0; }  // seeded
};
namespace inner {
int main() { return 1; }  // seeded
}  // namespace inner
// A type may be called main, but its constructor is a function named main followed by an opening parenthesis.
struct main {
  explicit main(std::int32_t v) : value(v) {}  // seeded
  std::int32_t value;
};
std::int32_t make() { return main{3}.value; }

}  // namespace kv::rule_6_0_4::bad_edge
