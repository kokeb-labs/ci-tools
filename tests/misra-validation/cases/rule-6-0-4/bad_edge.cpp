// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_0_4::bad_edge {

struct App {
  std::int32_t main() const { return 0; }  // a member function named main
};
namespace inner {
int main() { return 1; }  // a namespace-scope main in a nested namespace
}  // namespace inner

}  // namespace kv::rule_6_0_4::bad_edge
